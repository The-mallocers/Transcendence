import re
from time import sleep
import traceback

from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.tournaments.models import Tournaments
from utils.enums import EventType
from utils.enums import RTables, ResponseError, ResponseAction
from utils.threads.matchmaking import tournament_queue
from utils.websockets.channel_send import asend_group_error, asend_group
from utils.websockets.services.services import BaseServices


class TournamentService(BaseServices):
    async def init(self, client, *args) -> bool:
        await super().init(client)
        self.service_group = f'{EventType.TOURNAMENT.value}_{client.id}'
        self.channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(client.id), key=str(EventType.TOURNAMENT.value))
        self.channel_name = self.channel_name.decode('utf-8')
        return True

    async def _handle_create_tournament(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
        else:
            try:
                data['data']['args']['host'] = str(client.id)
                tournament = await Tournaments.create_tournament(data['data']['args'], runtime=True)
                tournament_queue.put(tournament)
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(tournament.code), self.channel_name)
                await self.redis.hset(name=RTables.HASH_TOURNAMENT_QUEUE(tournament.code), key=str(client.id), value=str(True))
                await asend_group(RTables.GROUP_TOURNAMENT(tournament.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_CREATED, {
                    'code': tournament.code,
                })
            except ValueError as e:
                await asend_group_error(self.service_group, ResponseError.KEY_ERROR, str(e))
            except Exception as e:
                self._logger.error(traceback.format_exc())
                await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_CREATE, str(e))

    async def _handle_join_tournament(self, data, client):
        code = data['data']['args']['code']
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if not await self.redis.exists(RTables.HASH_TOURNAMENT_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_EXIST)
        else:
            if await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('is_public')) == 'True':
                return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
            if await self.redis.hget(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_TOURNAMENT)
            else:
                await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id), 'True')
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), self.channel_name)
                await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_JOIN)
    
    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.PONG)

    async def _handle_leave_tournament(self, data, client):
        pass
    
    async def _handle_list_players(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            clients = await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_LIST, clients)
        else:
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
    
    
    async def _handle_tournament_info(self, data, client):
        sleep(1)
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
            # try:
            tournament_info = await self.tournament_info_helper(tournament_info)
            # except:
            #     print("EXCEPTION CASSE LES C")
            #     await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
            #     return
            print(tournament_info)
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_INFO, tournament_info)
        else:
            print("CHUIS PAS DANS LA QUEUE ?")
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)

    @staticmethod
    async def tournament_info_helper(tournament):
        tournament_ids = tournament['clients']
        title = tournament['title']
        max_clients = int(tournament['max_clients'])
        players_infos = await Clients.get_tournament_clients_infos(tournament_ids)
        roomInfos = {
            "title": title,
            "max_clients": max_clients,
            "players_infos": players_infos
        }
        return roomInfos


    # @staticmethod
    # async def tournament_info_helper(tournament):
    #     print("tournament = ", tournament)
    #     tournament_ids = tournament['clients']
    #     title = tournament['title']
    #     max_clients = int(tournament['max_clients'])

    #     print("tournament", tournament)
    #     print("title:", title)
    #     print("tournament_players:", tournament_ids)
    #     players_infos = [] 
    #     for id in tournament_ids:
    #         client = await Clients.aget_client_by_id(id)
    #         infos  = { 
    #             "id" : client.id,
    #             "nickname" : client.profile.username,
    #             "avatar" : client.profile.profile_picture.url,
    #             "trophee" : '/media/rank_icon/' + client.get_rank(client.stats.mmr) + ".png",
    #             "mmr" : client.stats.mmr,
    #         }
    #         players_infos.append(infos)

    #     roomInfos = {
    #         "title" : title,
    #         "max_clients" : max_clients,
    #         "players_infos" : players_infos
    #     }
    #     print("roomInfos:" , roomInfos)
    #     return roomInfos

    async def _handle_list_tournament(self, data, client):
        cursor, keys = await self.redis.scan(cursor=cursor, match=RTables.JSON_TOURNAMENT('*'))
        tournaments = []
        for key in keys:
            code = re.search(rf'{RTables.JSON_TOURNAMENT("")}(\w+)$', key.decode('utf-8')).group(1)
            
        if cursor == 0:
            return

    async def _handle_start_tournament(self, data, client):
        pass    
    
    async def _handle_get_tournament_clients(self, data, client):
        pass

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))

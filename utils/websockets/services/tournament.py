import re
from time import sleep
import traceback

from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.tournaments.models import Tournaments
from utils.enums import EventType
from utils.enums import RTables, ResponseError, ResponseAction
from utils.pong.objects import score
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
                tournament = await Tournaments.create_tournament(data['data']['args'], self.redis, runtime=True)
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
            client_list = [await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))]
            print("client list when join: ", client_list)
            if await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('max_clients')) < len(client_list):
                return await asend_group_error(self.service_group, ResponseError.TOURNAMENT_FULL)
            else:
                await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id), 'True')
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), self.channel_name)
                await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_JOIN, code)
    
    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.PONG)

    async def _handle_invite_friend(self, data, client):
        try:
            target_id = data['data']['args']['friend_id']
            target = await Clients.aget_client_by_id(target_id)
            
            if target is None:
                return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
            
            queues = await Clients.acheck_in_queue(client, self.redis)
            if not queues or RTables.HASH_TOURNAMENT_QUEUE('') not in str(queues):
                return await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
            
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            
            if await self.redis.hexists(RTables.HASH_TOURNAMENT_QUEUE(code), str(target.id)):
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_TOURNAMENT)
            
            # Check if invitation already exists
            invitation_key = f"{RTables.HASH_TOURNAMENT_INVITATION}:{code}:{target.id}"
            if await self.redis.exists(invitation_key):
                return await asend_group_error(self.service_group, ResponseError.INVITATION_ALREADY_SENT)
                
            # Block invitations if target has blocked client or vice versa
            client_friend_table = await client.get_friend_table()
            target_friend_table = await target.get_friend_table()
            
            if await client_friend_table.ais_blocked(target.id) or await target_friend_table.ais_blocked(client.id):
                return await asend_group_error(self.service_group, ResponseError.BLOCKED_USER)
                
            # Create the invitation
            invitation_key = f"{RTables.HASH_TOURNAMENT_INVITATION}:{code}:{target.id}"
            await self.redis.hset(invitation_key, "inviter_id", str(client.id))
            await self.redis.hset(invitation_key, "tournament_code", code)
            await self.redis.hset(invitation_key, "status", "pending")
            
            tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
            
            await asend_group(RTables.GROUP_NOTIF(target.id), 
                            EventType.NOTIFICATION, 
                            ResponseAction.TOURNAMENT_INVITATION, 
                            {
                                "sender": str(client.id),
                                "username": await client.aget_profile_username(),
                                "tournament_code": code,
                                "tournament_name": tournament_info['title']
                            })
            
            await asend_group(self.service_group, 
                            EventType.TOURNAMENT,
                            ResponseAction.TOURNAMENT_INVITATION_SENT,
                            {
                                "target": str(target.id),
                                "target_name": await target.aget_profile_username()
                            })
        
        except Exception as e:
            self._logger.error(traceback.format_exc())
            await asend_group_error(self.service_group, ResponseError.INTERNAL_ERROR, str(e))

    async def _handle_leave_tournament(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYER_LEFT)
        else:
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
    
    async def _handle_list_players(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            clients = await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_LIST, clients)
        else:
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
    
    
    async def _handle_tournament_info(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
            try:
                tournament_info = await self.tournament_info_helper(tournament_info, code)
            except:
                await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
                return
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_INFO, tournament_info)
        else:
            print("CHUIS PAS DANS LA QUEUE ?")
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)


    @staticmethod
    async def tournament_info_helper(tournament, code):
        tournament_ids = tournament['clients']
        title = tournament['title']
        max_clients = int(tournament['max_clients'])
        scoreboard = tournament['scoreboards']
        players_infos = await Clients.get_tournament_clients_infos(tournament_ids)
        roomInfos = {
            "title": title,
            "max_clients": max_clients,
            "players_infos": players_infos,
            "code": code,
            "scoreboard": scoreboard,
        }
        # print("roomInfos: ", roomInfos)
        return roomInfos

    async def _handle_list_tournament(self, data, client):
        cursor = 0
        all_tournaments = []
        
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=RTables.JSON_TOURNAMENT('*'))    
            for key in keys:
                code = re.search(rf'{RTables.JSON_TOURNAMENT("")}(\w+)$', key.decode('utf-8')).group(1)
                tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
                tournament_info = await self.tournament_info_helper(tournament_info, code)
                all_tournaments.append(tournament_info)
            if cursor == 0:
                break
        await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_LIST, all_tournaments)

    async def _handle_start_tournament(self, data, client):
        pass    
    
    async def _handle_get_tournament_clients(self, data, client):
        pass

    async def disconnect(self, client):
        print("IN DISCONNECT OF TOURNAMENT SERVICE")
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))
        # await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_UPDATE) #Sending the message to the others to check for updates.
            # tournament = Tournaments.get_tournament_by_code(code)
        #ADD the fact we want to change the status of the tournament from DB

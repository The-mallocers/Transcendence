import re
import traceback

from asgiref.sync import sync_to_async

from apps.client.models import Clients
from apps.tournaments.models import Tournaments
from utils.enums import EventType
from utils.enums import RTables, ResponseError, ResponseAction
from utils.threads.tournament import TournamentThread
from utils.util import create_tournament_id
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
            tournament = await sync_to_async(TournamentThread)(client)
            try:
                tournament.title = data['data']['args']['name']
                tournament.max_player = data['data']['args']['max_players']
                tournament.points_to_win = data['data']['args']['points_to_win']
                tournament.public = data['data']['args']['public']
                tournament.bots = data['data']['args']['bots']
                tournament.timer = data['data']['args']['timer']
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(tournament.code), self.channel_name)
                await sync_to_async(tournament.add_client)(client)
                await sync_to_async(tournament.start)()
            except KeyError as e:
                await asend_group_error(self.service_group, ResponseError.MISSING_KEY, f'{ResponseError.MISSING_KEY}: {str(e)}')
                tournament.stop()
            except Exception as e:
                traceback.print_exc()
                await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_CREATE, str(e))
                tournament.stop()

    async def _handle_join_tournament(self, data, client):
        code = data['data']['args']['code']
        tournament: Tournaments = await Tournaments.aget_tournament_by_id(code)
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if not await self.redis.exists(RTables.HASH_TOURNAMENT_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_EXIST)
        if not await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) and tournament.public is False:
            return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_TOURNAMENT)
            else:
                await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id), 'True')
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), self.channel_name)
                await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_JOIN)
                await asend_group(RTables.GROUP_TOURNAMENT(code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYER_JOIN, {
                    'id': client.id
                })

    async def _handle_leave_tournament(self, data, client):
        pass

    async def _handle_list_tournament(self, data, client):
        pass

    async def _handle_start_tournament(self, data, client):
        pass

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            tournament = await Tournaments.aget_tournament_by_id(code)
            if tournament:
                await tournament.adelete()
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))

import re
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

    async def _handle_list_tournament(self, data, client):
        pass

    async def _handle_start_tournament(self, data, client):
        pass

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))

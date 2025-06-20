import traceback

from asgiref.sync import sync_to_async

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.threads.matchmaking import local_queue
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients, *args):
        self.service_group = f'{EventType.GAME.value}_{client.id}'
        return await super().init(client)

    # ════════════════════════════════════ Online ════════════════════════════════════ #

    async def _handle_join_queue(self, data, client: Clients):
        try:
            if queue := await Clients.acheck_in_queue(client, self.redis):
                if await self.redis.hget(RTables.HASH_TOURNAMENT_QUEUE(queue.decode('utf-8')), str(client.id)) == 'False':
                    await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(queue.decode('utf-8')), str(client.id), 'True')
                    await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)
                return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
            if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
                return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
            else:
                await self.redis.hset(name=RTables.HASH_G_QUEUE, key=str(client.id), value=await client.aget_mmr())
                await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)
        except:
            return await asend_group_error(self.service_group, ResponseError.JOINING_ERROR)

    async def _handle_leave_queue(self, data, client: Clients):
        if await Clients.acheck_in_queue(client, self.redis) is RTables.HASH_G_QUEUE:
            await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(self.service_group, ResponseError.NOT_IN_QUEUE)

    # ════════════════════════════════════ Duels ═════════════════════════════════════ #


    async def _handle_leave_duel(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues is not RTables.HASH_G_QUEUE.value and queues is not None:
            await self.redis.delete(queues)
            await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(self.service_group, ResponseError.NOT_IN_QUEUE)

    # ════════════════════════════════════ Duels ═════════════════════════════════════ #
    async def _handle_local_game(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
        else:
            try:
                game = await sync_to_async(Game.create_game)(runtime=True)
                game.local = True
                game.points_to_win = data['data']['args']['points_to_win']
                game.pL = Player.create_player(client)
                game.pR = Player.create_player(client)
                local_queue.put(game)
                # await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(tournament.code), self.channel_name)
                await self.redis.hset(name=RTables.HASH_LOCAL_QUEUE, key=str(client.id), value=str(True))
                await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.GAME_CREATED)
            except ValueError as e:
                await asend_group_error(self.service_group, ResponseError.KEY_ERROR, str(e))
            except Exception as e:
                # self._logger.error(traceback.format_exc())
                await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_CREATE, str(e))

    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.PONG)

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            if queues is RTables.HASH_G_QUEUE:
                await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            elif RTables.HASH_TOURNAMENT_QUEUE('') in queues.decode('utf-8'):
                await self.redis.hset(queues.decode('utf-8'), str(client.id), str(False))
            else:
                await self.redis.delete(queues)

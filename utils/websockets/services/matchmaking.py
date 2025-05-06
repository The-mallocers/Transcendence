from asgiref.sync import sync_to_async

from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.util import create_game_id
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients, *args):
        print('init matchmaking')
        self.service_group = f'{EventType.GAME.value}_{client.id}'
        return await super().init(client)

    # ════════════════════════════════════ Online ════════════════════════════════════ #

    async def _handle_join_queue(self, data, client: Clients):
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
        else:
            await self.redis.hset(name=RTables.HASH_G_QUEUE, key=str(client.id), value=await client.aget_mmr())
            await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients):
        if await Clients.acheck_in_queue(client, self.redis) is RTables.HASH_G_QUEUE:
            await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(self.service_group, ResponseError.NOT_IN_QUEUE)

    # ════════════════════════════════════ Duels ═════════════════════════════════════ #
    
    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.PONG)

    async def _handle_leave_duel(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues is not RTables.HASH_G_QUEUE.value and queues is not None:
            await self.redis.delete(queues)
            await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(self.service_group, ResponseError.NOT_IN_QUEUE)

    async def disconnect(self, client):
        print("in disconnect of matchmaking")
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            if queues is RTables.HASH_G_QUEUE:
                await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            else:
                await self.redis.delete(queues)

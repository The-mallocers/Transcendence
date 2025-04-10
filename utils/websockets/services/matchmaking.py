from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.util import create_game_id
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients):
        return await super().init()

    async def _handle_join_queue(self, data, client: Clients):
        if await self.redis.hget(name=RTables.HASH_G_QUEUE, key=str(client.id)) is not None:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREAY_IN_GAME)
        else:
            await self.redis.hset(name=RTables.HASH_G_QUEUE, key=str(client.id), value=await client.aget_mmr())
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients):
        if await self.redis.hget(name=RTables.HASH_G_QUEUE, key=str(client.id)) is not None:
            await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            await self.redis.hdel(RTables.HASH_CLIENT(client.id), str(EventType.GAME.value))
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NOT_IN_QUEUE)

    async def _handle_create_duel(self, data, client: Clients):
        target = await Clients.aget_client_by_id(data['data']['args']['target'])
        if target is None:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.TARGET_NOT_FOUND)
        if target is client:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.DUEL_HIMSELF)
        else:
            duel_code = create_game_id()
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(client.id), value=str(True))
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(target.id), value=str(False))
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.DUEL_CREATED, {
                'code': duel_code
            })

    async def _handle_join_duel(self, data, client: Clients):
        pass

    async def _handle_leave_duel(self, data, client: Clients):
        pass

    async def handle_disconnect(self, client):
        if self.redis:
            await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
        await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)

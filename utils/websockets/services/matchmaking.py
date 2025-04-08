from channels.layers import get_channel_layer

from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients):
        await super().init()
        channel_layer = get_channel_layer()
        channel_name = await self.redis.hget(name="consumers_channels", key=str(client.id))
        await channel_layer.group_add(str(client.id), channel_name.decode('utf-8'))
        return True

    async def _handle_join_queue(self, data, client: Clients):
        if await self.redis.hget(name="matchmaking_queue", key=str(client.id)) is not None:
            await asend_group_error(client.id, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name='player_game', key=str(client.id)) is not None:
            await asend_group_error(client.id, ResponseError.ALREAY_IN_GAME)
        else:
            await self.redis.hset(name="matchmaking_queue", key=str(client.id), value=5)
            await asend_group(client.id, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients):
        if await self.redis.hget(name="matchmaking_queue", key=str(client.id)) is not None:
            await self.redis.hdel("matchmaking_queue", str(client.id))
            await asend_group(client.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            await asend_group_error(client.id, ResponseError.NOT_IN_QUEUE)

    async def handle_disconnect(self, client):
        await self.redis.hdel("matchmaking_queue", str(client.id))
        await asend_group(client.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)

from channels.layers import get_channel_layer

from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction
from utils.websockets.channel_send import send_group
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients, player: Player):
        channel_layer = get_channel_layer()
        channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
        await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))

    async def _handle_join_queue(self, data, client: Clients, player: Player):
        await self._redis.hset(name="matchmaking_queue", key=str(player.id), value=player.stats.mmr)
        await send_group(client.id, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients, player: Player):
        await self._redis.hdel("matchmaking_queue", str(player.id))
        await send_group(client.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)

    async def _handle_disconnect(self):
        pass

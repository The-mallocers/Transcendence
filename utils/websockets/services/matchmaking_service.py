from channels.layers import get_channel_layer

from apps.player.manager import PlayerManager
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction, ResponseError
from utils.websockets.channel_send import send_group, send_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients, player: Player):
        await super().init()
        channel_layer = get_channel_layer()
        channel_name = await self.redis.hget(name="consumers_channels", key=str(client.id))
        await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))
        return True

    async def _handle_join_queue(self, data, client: Clients, player: Player):
        if await self.redis.hget(name="matchmaking_queue", key=str(player.id)) is not None:
            await send_group_error(client.id, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name='player_game', key=str(player.id)) is not None:
            await send_group_error(client.id, ResponseError.ALREAY_IN_GAME)
        else:
            await self.redis.hset(name="matchmaking_queue", key=str(player.id), value=player.stats.mmr)
            await send_group(client.id, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients, player: Player):
        if await self.redis.hget(name="matchmaking_queue", key=str(player.id)) is not None:
            await self.redis.hdel("matchmaking_queue", str(player.id))
            await send_group(client.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            await send_group_error(client.id, ResponseError.NOT_IN_QUEUE)

    async def handle_disconnect(self, client):
        player = await PlayerManager.get_player_from_client_db(client.id)
        await self.redis.hdel("matchmaking_queue", str(player.id))
        await send_group(client.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)

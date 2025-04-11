from asgiref.sync import sync_to_async

from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.util import create_game_id
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class MatchmakingService(BaseServices):
    async def init(self, client: Clients):
        return await super().init()

    # ════════════════════════════════════ Online ════════════════════════════════════ #

    async def _handle_join_queue(self, data, client: Clients):
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREAY_IN_GAME)
        else:
            await self.redis.hset(name=RTables.HASH_G_QUEUE, key=str(client.id), value=await client.aget_mmr())
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data, client: Clients):
        if await Clients.acheck_in_queue(client, self.redis) is RTables.HASH_G_QUEUE:
            await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NOT_IN_QUEUE)

    # ════════════════════════════════════ Duels ═════════════════════════════════════ #

    async def _handle_create_duel(self, data, client: Clients):
        # ── Target Check ──────────────────────────────────────────────────────────── #
        target = await Clients.aget_client_by_id(data['data']['args']['target'])
        if target is None:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.TARGET_NOT_FOUND)
        if target.id == client.id:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.DUEL_HIMSELF)
        target_queues = await Clients.acheck_in_queue(target, self.redis)
        if target_queues is not RTables.HASH_G_QUEUE.value and target_queues is not None:
            if await self.redis.hexists(target_queues, str(target.id)):
                return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_INVITED)
        # ── Client Check ──────────────────────────────────────────────────────────── #
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREAY_IN_GAME)
        else:
            duel_code = await sync_to_async(create_game_id)()
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(client.id), value=str(True))
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(target.id), value=str(False))
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.DUEL_CREATED, {
                'code': duel_code
            })

    async def _handle_join_duel(self, data, client: Clients):
        code = data['data']['args']['code']
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_IN_QUEUE)
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(code)):
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.DUEL_NOT_EXIST)
        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) is False:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_DUEL_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_JOIN_DUEL)
            else:
                await self.redis.hset(RTables.HASH_DUEL_QUEUE(code), str(client.id), 'True')
                await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.DUEL_JOIN)




    async def _handle_leave_duel(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues is not RTables.HASH_G_QUEUE.value and queues is not None:
            await self.redis.delete(queues)
            await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)
        else:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NOT_IN_QUEUE)

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            if queues is RTables.HASH_G_QUEUE:
                await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            else:
                await self.redis.delete(queues)

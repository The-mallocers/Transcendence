import re
import traceback
from datetime import timedelta

from apps.client.models import Clients
from apps.tournaments.models import Tournaments
from utils.enums import RTables, ResponseError, EventType, ResponseAction
from utils.websockets.channel_send import asend_group_error, asend_group
from utils.enums import EventType
from utils.websockets.services.services import BaseServices


class TournamentService(BaseServices):
    async def init(self, client, *args) -> bool:
        self.service_group = f'{EventType.TOURNAMENT.value}_{client.id}'
        return await super().init(client)

    async def _handle_create_tournament(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREAY_IN_GAME)
        else:
            try:
                name = data['data']['args']['name']
                max_players = data['data']['args']['max_players']
                points_to_win = data['data']['args']['points_to_win']
                public = data['data']['args']['public']
                bots = data['data']['args']['bots']
                timer = data['data']['args']['timer']
                tournament = await Tournaments.objects.acreate(
                    name=name if name.strip() else f"{await client.aget_profile_username()}'s rooms",
                    host=client,
                    max_players=max_players,
                    public=public,
                    bots=bots,
                    points_to_win=points_to_win,
                    timer=timedelta(seconds=timer)
                )
                await self.redis.hset(name=RTables.HASH_TOURNAMENT_QUEUE(tournament.id), key=str(client.id), value=str(True))
                await asend_group(RTables.GROUP_CLIENT(client.id), EventType.MATCHMAKING, ResponseAction.TOURNAMENT_CREATED, {
                    'code': tournament.id,
                    'name': tournament.name
                })
            except KeyError as e:
                await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.MISSING_KEY, str(e))
            except Exception as e:
                traceback.print_exc()
                await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.TOURNAMENT_NOT_CREATE, str(e))

    async def _handle_join_tournament(self, data, client):
        pass

    async def _handle_leave_tournament(self, data, client):
        pass

    async def _handle_list_tournament(self, data, client):
        pass

    async def _handle_start_tournament(self, data, client):
        pass

    async def disconnect(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            if queues is RTables.HASH_G_QUEUE:
                await self.redis.hdel(RTables.HASH_G_QUEUE, str(client.id))
            else:
                code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
                tournament = await Tournaments.aget_tournament_by_id(code)
                self._logger.info(tournament)
                if tournament:
                    await tournament.adelete()
                await self.redis.delete(queues)

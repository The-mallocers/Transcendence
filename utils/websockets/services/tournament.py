import re
from time import sleep
import traceback

from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.game.models import Game
from apps.tournaments.models import Tournaments
from utils.enums import EventType, GameStatus, PlayerSide, TournamentStatus
from utils.enums import RTables, ResponseError, ResponseAction
from utils.pong.objects import score
from utils.threads.matchmaking import tournament_queue
from utils.websockets.channel_send import asend_group_error, asend_group
from utils.websockets.services.services import BaseServices


class TournamentService(BaseServices):
    async def init(self, client, *args) -> bool:
        await super().init(client)
        self.service_group = f'{EventType.TOURNAMENT.value}_{client.id}'
        self.channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(client.id), key=str(EventType.TOURNAMENT.value))
        self.channel_name = self.channel_name.decode('utf-8')
        await self._helper_tournament_connection(client)
        return True


    async def _helper_tournament_connection(self, client):
        code = await self.check_if_socket_in_tournament(client)
        if code:
            await self.add_socket_to_group(code)

    async def check_if_socket_in_tournament(self, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        code = None
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
        return code

    async def add_socket_to_group(self, code):
        await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), self.channel_name)


    async def _handle_create_tournament(self, data, client: Clients):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
        else:
            try:
                data['data']['args']['host'] = str(client.id)
                tournament = await Tournaments.create_tournament(data['data']['args'], self.redis, runtime=True)
                tournament_queue.put(tournament)
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(tournament.code), self.channel_name)
                await self.redis.hset(name=RTables.HASH_TOURNAMENT_QUEUE(tournament.code), key=str(client.id), value=str(True))
                online_clients = await self.get_all_online_clients()
                for online_client in online_clients:
                    if online_client == RTables.GROUP_CLIENT(client.id):
                        await asend_group(RTables.GROUP_TOURNAMENT(tournament.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_CREATED,{
                                  'code': tournament.code,})
                    else:
                        await asend_group(online_client, EventType.TOURNAMENT, ResponseAction.NEW_TOURNAMENTS, {
                                "code": tournament.code})
            except ValueError as e:
                await asend_group_error(self.service_group, ResponseError.KEY_ERROR, str(e))
            except Exception as e:
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
            client_list = [await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))]
            if await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('max_clients')) < len(client_list):
                return await asend_group_error(self.service_group, ResponseError.TOURNAMENT_FULL)
            else:
                await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id), 'True')
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), self.channel_name)
                await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_JOIN, code)

    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.PONG)

    async def _handle_invite_friend(self, data, client):
        try:
            target_id = data['data']['args']['friend_id']
            target = await Clients.aget_client_by_id(target_id)
            
            if target is None:
                return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
            
            queues = await Clients.acheck_in_queue(client, self.redis)
            if not queues or RTables.HASH_TOURNAMENT_QUEUE('') not in str(queues):
                return await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
            
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            
            if await self.redis.hexists(RTables.HASH_TOURNAMENT_QUEUE(code), str(target.id)):
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_TOURNAMENT)
            
            # Check if invitation already exists
            invitation_key = f"{RTables.HASH_TOURNAMENT_INVITATION}:{code}:{target.id}"
            if await self.redis.exists(invitation_key):
                return await asend_group_error(self.service_group, ResponseError.INVITATION_ALREADY_SENT)
                
            # Block invitations if target has blocked client or vice versa
            client_friend_table = await client.get_friend_table()
            target_friend_table = await target.get_friend_table()
            
            if await client_friend_table.ais_blocked(target.id) or await target_friend_table.ais_blocked(client.id):
                return await asend_group_error(self.service_group, ResponseError.BLOCKED_USER)
                
            # Create the invitation
            invitation_key = f"{RTables.HASH_TOURNAMENT_INVITATION}:{code}:{target.id}"
            await self.redis.hset(invitation_key, "inviter_id", str(client.id))
            await self.redis.hset(invitation_key, "tournament_code", code)
            await self.redis.hset(invitation_key, "status", "pending")
            
            tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
            
            await asend_group(RTables.GROUP_NOTIF(target.id), 
                            EventType.NOTIFICATION, 
                            ResponseAction.TOURNAMENT_INVITATION, 
                            {
                                "sender": str(client.id),
                                "username": await client.aget_profile_username(),
                                "tournament_code": code,
                                "tournament_name": tournament_info['title']
                            })
            
            await asend_group(self.service_group, 
                            EventType.TOURNAMENT,
                            ResponseAction.TOURNAMENT_INVITATION_SENT,
                            {
                                "target": str(target.id),
                                "target_name": await target.aget_profile_username()
                            })
        
        except Exception as e:
            self._logger.error(traceback.format_exc())
            await asend_group_error(self.service_group, ResponseError.INTERNAL_ERROR, str(e))

    async def _handle_leave_tournament(self, data, client):
        #This used to be disconnected code
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))
            
            # Check if client is in a game
            game_code = await self.redis.hget(RTables.HASH_MATCHES, str(client.id))
            if game_code is not None:
                # Client is in a game, handle the forfeit
                game_code_str = game_code.decode('utf-8')
                try:
                    # Get game data
                    player_left = await self.redis.json().get(RTables.JSON_GAME(game_code_str), Path(f'{PlayerSide.LEFT.value}.id'))
                    player_right = await self.redis.json().get(RTables.JSON_GAME(game_code_str), Path(f'{PlayerSide.RIGHT.value}.id'))
                    point_to_win = await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('points_to_win'))
                    
                    # Update score based on which player left
                    if player_left == str(client.id):
                        await self.redis.json().set(RTables.JSON_GAME(game_code_str), Path(f'{PlayerSide.RIGHT.value}.score'), point_to_win)
                        self._logger.info(f"Player {client.id} (LEFT) left tournament game {game_code_str}")
                    elif player_right == str(client.id):
                        await self.redis.json().set(RTables.JSON_GAME(game_code_str), Path(f'{PlayerSide.LEFT.value}.score'), point_to_win)
                        self._logger.info(f"Player {client.id} (RIGHT) left tournament game {game_code_str}")
                    
                    # Optional: Mark the game as ending
                    # await self.redis.json().set(RTables.JSON_GAME(game_code_str), Path('status'), GameStatus.ENDING)
                except Exception as e:
                    self._logger.error(f"Error handling game forfeit on tournament leave: {str(e)}")

        return await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_LEFT)
    
    async def _handle_list_players(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            clients = await self.redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_LIST, clients)
        else:
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)


    async def _handle_tournament_info(self, data, client):
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            tournament_info = await self.redis.json().get(RTables.JSON_TOURNAMENT(code))
            try:
                tournament_info = await self.tournament_info_helper(tournament_info, code, client)
            except Exception as e:
                await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)
                return
            await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_INFO, tournament_info)
        else:
            await asend_group_error(self.service_group, ResponseError.NOT_IN_TOURNAMENT)


    async def tournament_info_helper(self, tournament, code, client):
        tournament_ids = tournament['clients']
        title = tournament['title']
        max_clients = int(tournament['max_clients'])
        scoreboard = tournament['scoreboards']
        host = tournament['host']
        players_infos = await Clients.get_tournament_clients_infos(tournament_ids)
        game_ready = await self.redis.hexists(RTables.HASH_MATCHES, str(client.id))
        print("game ready is ", game_ready)
        roomInfos = {
            "title": title,
            "max_clients": max_clients,
            "players_infos": players_infos,
            "code": code,
            "host" : host,
            "scoreboard": scoreboard,
            "game_ready": game_ready,
        }
        return roomInfos

    async def _handle_list_tournament(self, data, client):
        tournaments_in_waitting = []

        async for key in self.redis.scan_iter(match=f'{RTables.JSON_TOURNAMENT("*")}'):
            key = key.decode('utf-8')
            tournament_json = await self.redis.json().get(key)
            tournament_code = re.search(rf'{RTables.JSON_TOURNAMENT("")}(\w+)$', key).group(1)
            tournament_status = TournamentStatus(await self.redis.json().get(key, Path('status')))
            tournament_info = await self.tournament_info_helper(tournament_json, tournament_code, client)
            if tournament_status is TournamentStatus.WAITING:
                tournaments_in_waitting.append(tournament_info)

        await asend_group(self.service_group, EventType.TOURNAMENT, ResponseAction.TOURNAMENT_LIST, tournaments_in_waitting)

    async def disconnect(self, client):
        await super().disconnect(client)

        # Remove this client's tournament service from Redis
        await self.redis.hdel(RTables.HASH_CLIENT(client.id), str(EventType.TOURNAMENT.value))

        # Handle any tournament-specific cleanup
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            await self.channel_layer.group_discard(RTables.GROUP_TOURNAMENT(code), self.channel_name)
            await self.redis.hdel(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id))

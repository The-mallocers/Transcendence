import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.game.models import Game, GameService
from apps.player.models import Player
from apps.shared.models import Clients


class WebSocketGame(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = GameService()
        self.game_group_id = None
        self.game: Game = None
        self.player: Player = None

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        client: Clients = await Clients.get(query_params.get('id', ['default'])[0])
        self.game: Game = await Game.get(query_params.get('game', ['default'])[0])

        if client is None:
            await self.close(code=403, reason='Client does not exist')
            return
        if self.game is None:
            await self.close(code=403, reason='Game does not exist')
            return

        self.player = client.player

        # ── Init ──────────────────────────────────────────────────────────────────────

        # if self.game.id not in await self.service.game_manager.get_game_list():
        #     self.game = await self.service.game_manager.create_game(in_tournament=False)
        #
        # if self.player.id not in self.service.player_manager.get_player_list():
        #     self.service.player_manager.init(self.player.id)
        #
        # # Join room group
        # self.game_group_id = f'group_{game_id}'
        # await self.channel_layer.group_add(self.game_group_id, self.channel_name)

        await self.accept()
        print("test")
        await self.close(code=2000)

    async def disconnect(self, close_code):
        if self.game_group_id:
            await self.channel_layer.group_discard(
                self.game_group_id,
                self.channel_name
            )
        # if self.client_id:
        #     await self.game_logic.handle_disconnect(self.room_id,
        #                                             self.client_id)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)

            response = await self.service.process_action(
                player=self.player,
                data=data,
                game=self.game
            )

            if 'error' in response:
                await self.send(text_data=json.dumps(response))
                await self.close(code=4000)
                return

            await self.channel_layer.group_send(
                self.game_group_id,
                {
                    'type': 'game_message',
                    'message': response,
                    'sender': self.player.id
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def game_message(self, event):
        message = event['message']
        if event['sender'] != self.player.id:
            await self.send(text_data=json.dumps(message))
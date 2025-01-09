import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        printf("Websocket connect: Trying to connect ...")
        await self.accept()
        print("WebSocket connected")

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: closed with code {close_code}")

    async def receive(self, text_data):
        printf("websocket received data:", text_data)
        data = json.loads(text_data)
        action = data.get('action')

        # This is some crap chat gpt wrote, will need to be modified.
        if action == 'move':
            position = data.get('position')  # Example client-sent data
            # Calculate new position on the server
            new_position = position + 1  # Simulating server-side movement
            await self.send(json.dumps({'new_position': new_position}))

from apps.chat.models import Rooms
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.chat import ChatService, uuid_global_room


class ChatConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ChatService()

    async def connect(self):
        await super().connect()
        if self.client:
            await self.channel_layer.group_add(str(uuid_global_room), self.channel_name)
            rooms = await Rooms.ASget_room_id_by_client_id(self.client.id)
            for room in rooms:
                await self.channel_layer.group_add(str(room), self.channel_name)

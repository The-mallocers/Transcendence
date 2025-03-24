from django.apps import AppConfig



class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'
    
    def post_migrate(self):
        from utils.websockets.services.chat_service import uuid_global_room
        from apps.shared.models import Clients
        from apps.chat.models import Rooms
        global_room, created = Rooms.objects.get_or_create(id=uuid_global_room)
        clients = Clients.objects.all()
        for client in clients:
            global_room.clients.add(client)
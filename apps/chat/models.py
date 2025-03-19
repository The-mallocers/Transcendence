import django.core.exceptions
from django.db import models, transaction
import uuid
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from asgiref.sync import sync_to_async

from apps.player.models import Player
from apps.shared.models import Clients
from apps.error.views import error

class Rooms(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)
    clients = models.ManyToManyField(Clients, related_name="rooms")
    admin = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, related_name='admin')
    created_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Room with id: {self.id}'

    async def add_client(self, client):
        try:
            # Utilisation de sync_to_async pour exécuter en tâche de fond
            await sync_to_async(self.clients.add)(client)
        except Exception as e:
            raise Exception(f"Erreur lors de l'ajout du client : {e}")

    @staticmethod
    async def create_room(id=None):
        try:
            return await sync_to_async(Rooms.objects.create)(id=id)
        except Exception as e:
            raise Exception(f"Erreur lors de la création de la salle : {e}")
        
    @staticmethod
    @sync_to_async
    def get_room_by_id(id: uuid.UUID):
        try:
            with transaction.atomic():
                return Rooms.objects.get(id=id)
        except Rooms.DoesNotExist:
            return None
        except ValidationError:
            return None

    @staticmethod
    @sync_to_async
    def get_id(room):
        try:
            with transaction.atomic():
                return room.id
        except Rooms.DoesNotExist:
            return None
        
    @staticmethod
    @sync_to_async
    def get_room_id_by_client_id(client_id):
        try:
            with transaction.atomic():
                return list(Rooms.objects.filter(clients__id=client_id).values_list('id', flat=True))  
        except Clients.DoesNotExist:
            return []
        
    @staticmethod
    @sync_to_async
    def get_clients_id_by_room_id(room_id):
        try:
            with transaction.atomic():
                # return list(Clients.objects.filter(rooms__id=room_id).values_list('id', flat=True))
                uuid_list = list(Clients.objects.filter(rooms__id=room_id).values_list('id', flat=True))
                return [str(uuid) for uuid in uuid_list]
        except Rooms.DoesNotExist:
            return []
    
    @staticmethod
    @sync_to_async  
    def get_player_from_client_db(client_id) -> Player | None:
        """Get player with client id from data base"""
        try:
            with transaction.atomic():
                return Clients.objects.select_related('player__stats').get(id=client_id).player
        except Clients.DoesNotExist:
            return None

            

class Messages(models.Model):
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Clients, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Messages: {self.content}'

    @staticmethod
    @sync_to_async
    def get_message_by_room(room):
        try:
            with transaction.atomic():
                return list(Messages.objects.filter(room__id=room.id))
        except Rooms.DoesNotExist:
            return []
        
    @sync_to_async
    def get_sender_id(self):
        try:
            with transaction.atomic():
                return self.sender.id
        except Exception:
            return None




from django.db import models, IntegrityError, transaction
import uuid
from django.utils import timezone
from django.db import models
from asgiref.sync import sync_to_async

from apps.shared.models import Clients

class Rooms(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)
    clients = models.ManyToManyField(Clients, related_name="rooms")
    created_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    async def add_client(self, client):
        try:
            # Utilisation de sync_to_async pour exécuter en tâche de fond
            await sync_to_async(self.clients.add)(client)
        except Exception as e:
            raise Exception(f"Erreur lors de l'ajout du client : {e}")

    @staticmethod
    async def create_room():
        try:
            return await sync_to_async(Rooms.objects.create)()
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

    @staticmethod
    @sync_to_async
    def get_id(room):
        try:
            with transaction.atomic():
                return room.id
        except Rooms.DoesNotExist:
            return None

class Messages(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)
    rooms = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Clients, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)



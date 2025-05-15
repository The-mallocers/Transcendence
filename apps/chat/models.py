import logging
import uuid

from asgiref.sync import sync_to_async
from django.db import models
from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone

from apps.client.models import Clients


class Rooms(models.Model):
    # Primary key
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
    def aget_room_id_by_client_id(client_id):
        try:
            with transaction.atomic():
                return list(Rooms.objects.filter(clients__id=client_id).values_list('id', flat=True))
        except Clients.DoesNotExist:
            return []

    @staticmethod
    def get_room_id_by_client_id(client_id):
        try:
            return list(Rooms.objects.filter(clients__id=client_id).values_list('id', flat=True))
        except Clients.DoesNotExist:
            return []

    @staticmethod
    def get_room_by_client_id(client_id):
        try:
            return list(Rooms.objects.filter(clients__id=client_id))
        except Clients.DoesNotExist:
            return []

    @staticmethod
    @sync_to_async
    def get_user_info_by_room_id(room_id):
        try:
            with transaction.atomic():
                users = Clients.objects.filter(rooms__id=room_id).select_related('profile').distinct()
                user_info = []
                for user in users:
                    profile_pic_url = user.profile.profile_picture.url if user.profile.profile_picture else "/static/assets/imgs/profile/default.png"
                    user_info.append({
                        'id': str(user.id),
                        'username': user.profile.username,
                        'profile_picture': profile_pic_url
                    })
                return user_info
        except Exception as e:
            import traceback
            logging.getLogger('MainThread').error(f"Error in get_user_info_by_room_id: {str(e)}")
            logging.getLogger('MainThread').error(traceback.format_exc())
            return []
    
    @staticmethod
    @sync_to_async
    def Aget_room_by_client_id(client_id):
        try:
            with transaction.atomic():
                query = Rooms.objects.filter(clients__id=client_id)
                return query.first()
        except Exception as e:
            raise Exception(f"Error getting room by client ID: {e}")
        except Clients.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_usernames_by_room_id(room_id):
        try:
            with transaction.atomic():
                username_list = list(
                    Clients.objects.filter(rooms__id=room_id).values_list('profile__username', flat=True))
                return username_list
        except Rooms.DoesNotExist:
            return []

    @staticmethod
    @sync_to_async
    def aget_user_by_room_id(room_id):
        try:
            with transaction.atomic():
                user_list = list(
                    Clients.objects.filter(rooms__id=room_id).values_list('id', flat=True))
                return user_list
        except Rooms.DoesNotExist:
            return []

    @staticmethod
    @sync_to_async
    def get_client_id_by_username(username):
        try:
            with transaction.atomic():
                client = Clients.objects.get(profile__username=username)
                return str(client.id)  # Retourne l'ID sous forme de chaîne
        except Clients.DoesNotExist:
            return None

    @sync_to_async
    def aget_target_by_room_id(self, client):
        try:
            with transaction.atomic():
                targetUser = Clients.objects.filter(rooms__id=self.id)
                if targetUser is not None:
                    targetUser = targetUser.exclude(id=client.id)
                return targetUser.first()
        except Exception as e:
            logging.getLogger('MainThread').error(f"Error retrieving target id in the room: {e}")
            return None

    @sync_to_async
    def adelete_room(self):
        try:
            with transaction.atomic():
                self.delete()
        except Clients.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def adelete_all_user_by_room_id(roomId):
        try:
            with transaction.atomic():
                room = Rooms.objects.get(id=roomId)
                # Clear all related clients (this removes the relationship, not the clients themselves)
                room.clients.clear()
            return True
        except Exception:
            return None


class Messages(models.Model):
    id = models.BigAutoField(primary_key=True)
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Clients, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField()
    send_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Messages: {self.content}'

    @staticmethod
    def get_message_by_room(room):
        try:
            return list(Messages.objects.filter(room__id=room.id))
        except Rooms.DoesNotExist:
            return []

    @staticmethod
    @sync_to_async
    def aget_message_by_room(room, target):
        try:
            with transaction.atomic():
                return list(Messages.objects.filter(room__id=room.id))
        except Exception as e:
            return None

    @sync_to_async
    def get_sender_id(self):
        try:
            with transaction.atomic():
                return self.sender.id
        except Exception:
            return None

    @staticmethod
    @sync_to_async
    def adelete_all_messages_by_room_id(roomId):
        try:
            with transaction.atomic():
                Messages.objects.filter(room_id=roomId).delete()
                return True
        except Exception:
            return None

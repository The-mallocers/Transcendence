import uuid

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction

from apps.client.models import Clients


class Friend(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
    email = models.EmailField(null=False, editable=True, blank=True)
    friends = models.ManyToManyField(Clients, related_name='friend_requests_as_friend', blank=True)
    pending_friends = models.ManyToManyField(Clients, related_name='friend_requests_as_pending', blank=True)
    blocked_users = models.ManyToManyField(Clients, related_name='blocked_by', blank=True)

    class Meta:
        # unique_together = ['friends', 'pending_friends']
        verbose_name_plural = 'Friend Requests'

    def __str__(self):
        return f"Friend Request with {self.id}"

    def delete(self, *args, **kwargs):
        self.friends.clear()
        self.pending_friends.clear()
        self.blocked_users.clear()
        super().delete(*args, **kwargs)

    @staticmethod
    def is_pending_friend(client, target):
        try:
            friend_obj = Friend.objects.get(id=client.friend.id)
            if not friend_obj.pending_friends.filter(id=target.id).exists() :
                return True
            return False
        except:
            return False

    @sync_to_async
    def add_pending_friend(self, client):
        try:
            with transaction.atomic():
                # if friend is not my friend i add it to pending_friend
                if not self.friends.filter(id=client.id).exists() and not self.pending_friends.filter(id=client.id).exists():
                    self.pending_friends.add(client)
                    self.save()
                    return client
        except Exception as e:
            raise Exception(f"Error retrieving friend request: {e}")

    @sync_to_async
    def accept_pending_friend(self, client):
        try:
            with transaction.atomic():
                # check if my friend is in pending
                pending_friend = self.pending_friends.filter(id=client.id).exists()
                if not pending_friend:
                    raise ValidationError("No pending friend with this id")
                # check if my friend is already my friend
                friend = self.friends.filter(id=client.id).exists()
                if friend:
                    raise ValidationError("Already Friend")
                self.friends.add(client)
                self.pending_friends.remove(client)
                self.save()
        except:
            raise ValidationError("")

    @sync_to_async
    def accept_other_friend(self, client):
        with transaction.atomic():
            self.friends.add(client)
            self.save()

    @sync_to_async
    def refuse_pending_friend(self, client):
        try:
            with transaction.atomic():
                self.pending_friends.remove(client)
        except:
            raise ValidationError("Friend not in pending")

    @sync_to_async
    def remove_friend(self, client):
        try:
            with transaction.atomic():
                if not self.friends.filter(id=client.id).exists():
                    raise ValidationError("Not friend with this user")
                self.friends.remove(client)
                self.save()
        except Exception as e:
            raise ValidationError("Failed to remove friend")

    # add friend to duel
    @sync_to_async
    def add_prending_duel(self, client):
        try:
            with transaction.atomic():
                if not self.pending_duel.filter(id=client.id).exists():
                    self.pending_duel.add(client)
                    self.save()
                    return client
        except Exception as e:
            return None

    @sync_to_async
    def get_blocked_users(self):
        try:
            with transaction.atomic():
                return self.blocked_users
        except Exception as e:
            return None

    @sync_to_async
    def block_user(self, target):
        try:
            with transaction.atomic():
                if not self.blocked_users.filter(id=target.id).exists():
                    self.blocked_users.add(target)
                    self.save()
        except Exception as e:
            return None

    @sync_to_async
    def unblock_user(self, target):
        try:
            with transaction.atomic():
                if self.blocked_users.filter(id=target.id).exists():
                    self.blocked_users.remove(target)
                    self.save()
        except Exception as e:
            return None

    @sync_to_async
    def user_is_block(self, target):
        try:
            with transaction.atomic():
                if self.blocked_users.filter(id=target.id).exists():
                    return True
                return False
        except Exception as e:
            return None
        
    @sync_to_async
    def ais_blocked(self, user_id):
        try:
            with transaction.atomic():
                is_blocked = self.blocked_users.filter(id=user_id).exists()
                return is_blocked
        except Exception as e:
            return False
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

    # def __str__(self):
    #     return f"Friend Request with {self.id}"

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
            print(f"Error adding pending friend: {e}")
            return None

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
                    print("already friends")
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
            print(f"Error removing friend: {e}")
            raise ValidationError("Failed to remove friend")
        
    #add friend to duel
    @sync_to_async
    def add_prending_duel(self, client):
        try:
            with transaction.atomic():
                if not self.pending_duel.filter(id=client.id).exists():
                    self.pending_duel.add(client)
                    self.save()
                    return client
        except Exception as e:
            print(f"Error adding pending duel: {e}")
            return None
    
    @sync_to_async
    def get_blocked_users(self):
        try:
            with transaction.atomic():
                return self.blocked_users
        except Exception as e:
            print(f"Error getting blocked users: {e}")
            return None
        
    @sync_to_async
    def block_user(self, target):
        try:
            with transaction.atomic():
                if not self.blocked_users.filter(id=target.id).exists():
                    self.blocked_users.add(target)
                    self.save()
        except Exception as e:
            print(f"Error adding block user: {e}")
            return None

    @sync_to_async
    def unblock_user(self, target):
        try:
            with transaction.atomic():
                if self.blocked_users.filter(id=target.id).exists():
                    self.blocked_users.remove(target)
                    self.save()
        except Exception as e:
            print(f"Error unblock user: {e}")
            return None
        
    @sync_to_async
    def user_is_block(self, target):
        try:
            with transaction.atomic():
                if self.blocked_users.filter(id=target.id).exists():
                    return True
                return False
        except Exception as e:
            print(f"Error unblock user: {e}")
            return None
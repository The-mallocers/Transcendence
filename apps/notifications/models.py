from django.db import models, IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
import logging
from asgiref.sync import sync_to_async

from apps.client.models import Clients

class Friend(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
    email = models.EmailField(null=False, editable=True, blank=True)
    friends = models.ManyToManyField(Clients, related_name='friend_requests_as_friend', blank=True)
    pending_friends = models.ManyToManyField(Clients, related_name='friend_requests_as_pending', blank=True)
    
    class Meta:
        # unique_together = ['friends', 'pending_friends']
        verbose_name_plural = 'Friend Requests'
    
    def __str__(self):
        return f"Friend Request with {self.id}"
    
    @sync_to_async
    def add_pending_friend(self, client):
        try:
            with transaction.atomic():
                #if friend is not my friend i add it to pending_friend
                if not self.friends.filter(id=client.id).exists() and not self.pending_friends.filter(id=client.id).exists():
                    print("entering in the adding pending friend")
                    self.pending_friends.add(client)
                    self.save()
                    return client
        except Exception as e:
            print(f"Error retrieving friend request: {e}")
            return None
    
    @sync_to_async
    def accept_pending_friend(self, client):
        try: 
            with transaction.atomic():
                print("in the accepting function")
                #check if my friend is in pending
                pending_friend = self.pending_friends.filter(id=client.id).exists()
                if not pending_friend:
                    print("no pending friend")
                    raise ValidationError("No pending friend with this id")
                #check if my friend is already my friend
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
            


        
    
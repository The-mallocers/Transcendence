from django.db import models
from django.contrib.postgres.fields import ArrayField
from asgiref.sync import sync_to_async
import uuid

from apps.shared.models import Clients

class FriendRequest(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.OneToOneField(Clients, primary_key=True, on_delete=models.CASCADE)
    friends = ArrayField(models.UUIDField(), blank=True, null=True, default=list)
    pending_friends = ArrayField(models.UUIDField(), blank=True, null=True, default=list)
    
    # Timestamps
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['friends', 'pending_friends']
        verbose_name_plural = 'Friend Requests'
    
    def __str__(self):
        return f"Friend Request with {len(self.friends)} friends and {len(self.pending_friends)} pending"
    
    @classmethod
    async def ASget_me(client):
        try:
            friend_request = await sync_to_async(FriendRequest.objects.get)(id=client)
            print(friend_request)
            return friend_request
        except:
            return None
    
    @classmethod
    def are_friends(cls, client1, client2):
        try:
            friend_request1 = cls.objects.get(id=client1)
            return client2 in friend_request1.friends
        except cls.DoesNotExist:
            return False
    
    def add_friend(self, friend_id):
        if friend_id not in self.friends:
            self.friends.append(friend_id)
            self.save()
    
    def remove_friend(self, friend_id):
        if friend_id in self.friends:
            self.friends.remove(friend_id)
            self.save()
    
    def add_pending_friend(self, friend_id):
        if friend_id not in self.pending_friends:
            self.pending_friends.append(friend_id)
            self.save()
    
    def remove_pending_friend(self, friend_id):
        if friend_id in self.pending_friends:
            self.pending_friends.remove(friend_id)
            self.save()
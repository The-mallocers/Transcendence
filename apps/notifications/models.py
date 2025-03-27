from django.db import models, IntegrityError, transaction
from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from asgiref.sync import sync_to_async

from apps.shared.models import Clients

class Friend(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
    email = models.EmailField(null=False, editable=True)
    friends = models.ManyToManyField(Clients, related_name='friend_requests_as_friend', blank=True)
    pending_friends = models.ManyToManyField(Clients, related_name='friend_requests_as_pending', blank=True)
    
    class Meta:
        # unique_together = ['friends', 'pending_friends']
        verbose_name_plural = 'Friend Requests'
    
    def __str__(self):
        return f"Friend Request with {self.id}"
    
    @staticmethod
    def are_friends(cls, client1, client2):
        try:
            friend_request1 = cls.objects.get(id=client1)
            return client2 in friend_request1.friends
        except cls.DoesNotExist:
            return False
    
    @sync_to_async
    def add_pending_friend(self, client):
        try:
            with transaction.atomic():
                if not self.friends.filter(id=client.id).exists():
                    print("entering in the adding pending friend")
                    self.pending_friends.add(client)
                    self.save()
        except Exception as e:
            print(f"Error retrieving friend request: {e}")
            return Noneast
    
    #for the accept friend=> need to accept on the current client that have the pending and add client
    #add the friend to the client being pending
    
    def add_friend(self, friend_id):
        if friend_id not in self.friends:
            self.friends.append(friend_id)
            self.save()
    
    def remove_friend(self, friend_id):
        if friend_id in self.friends:
            self.friends.remove(friend_id)
            self.save()
    
    def remove_pending_friend(self, friend_id):
        if friend_id in self.pending_friends:
            self.pending_friends.remove(friend_id)
            self.save()
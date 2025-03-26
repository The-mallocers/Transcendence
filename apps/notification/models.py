from django.db import models
import uuid

class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Sender of the friend request
    sender = models.ForeignKey(
        'Clients', 
        on_delete=models.CASCADE, 
        related_name='sent_friend_requests'
    )
    
    # Receiver of the friend request
    receiver = models.ForeignKey(
        'Clients', 
        on_delete=models.CASCADE, 
        related_name='received_friend_requests'
    )
    
    # Status of the relationship
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked')
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['sender', 'receiver']
        verbose_name_plural = 'Friend Requests'
    
    def __str__(self):
        return f"Friend Request: {self.sender} to {self.receiver} - {self.status}"
    
    @classmethod
    def get_friends(cls, client):
        """
        Get all accepted friends for a client
        """
        # Find all accepted requests where client is either sender or receiver
        friends_as_sender = cls.objects.filter(
            sender=client, 
            status='accepted'
        ).values_list('receiver', flat=True)
        
        friends_as_receiver = cls.objects.filter(
            receiver=client, 
            status='accepted'
        ).values_list('sender', flat=True)
        
        # Combine and return unique friends
        return list(set(list(friends_as_sender) + list(friends_as_receiver)))
    
    @classmethod
    def are_friends(cls, client1, client2):
        """
        Check if two clients are friends
        """
        return cls.objects.filter(
            (models.Q(sender=client1, receiver=client2) | 
             models.Q(sender=client2, receiver=client1)),
            status='accepted'
        ).exists()
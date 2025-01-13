import uuid

from django.db import models

from account.models import Profile, default_profile
from admin.models import Admin
from auth.models import Auth, default_auth


class Client(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Joined tables
    auth = models.ForeignKey(Auth, on_delete=models.CASCADE, default=1)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True)
    # log = models.ForeignKey(Log, on_delete=models.CASCADE)

    #Funcions
    @staticmethod
    def get_client(req):
        client_id = req.session.get('client_id')
        if client_id is None:
            return None
        user = Client.objects.get(id=client_id)
        return user
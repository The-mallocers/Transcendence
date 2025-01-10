import uuid

import bcrypt
from django.db import models

class Auth(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Secondary key
    password = models.CharField(max_length=512, default='1234')
    session_user = models.UUIDField(default=uuid.uuid4())

    #Functions
    def update(self, data, value):
        match data:
            case "password":
                self.password = value
            case "session_user":
                self.session_user = value
            case _:
                return None
        self.save()

def default_auth():
    salt = bcrypt.gensalt(prefix=b'2b')
    default_pass = 'default'
    pwd = bcrypt.hashpw(default_pass.encode('utf-8'), salt).decode("utf-8")
    auth = Auth.objects.create()
    return auth
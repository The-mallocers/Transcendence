import uuid

import bcrypt
from django.db import models


class Password(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Secondary key
    password = models.CharField(max_length=512, default='1234')

    #Functions
    def update(self, data, value):
        match data:
            case "password":
                self.password = value
            case _:
                return None
        self.save()
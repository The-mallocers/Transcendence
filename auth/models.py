import uuid

import bcrypt
from django.db import models


class Password(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Secondary key
    password = models.CharField(max_length=512, null=False, editable=True)

    #Functions
    def save(self, *args, **kwargs):
        salt = bcrypt.gensalt(prefix=b'2b')
        if not self.password.startswith('$2b$'):
            self.password = bcrypt.hashpw(self.password.encode('utf-8'),
                                          salt).decode('utf-8')
        super().save(*args, **kwargs)

    def update(self, data, value) -> None:
        match data:
            case "password":
                self.password = value
            case _:
                return None
        self.save()

    def check_pwd(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'),
                              self.password.encode('utf-8'))

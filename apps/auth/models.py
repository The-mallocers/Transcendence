import uuid

import bcrypt
import pyotp
from django.db import models


class Password(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)

    #Secondary key
    password = models.CharField(max_length=512, null=False, editable=True)
    old_password = models.CharField(max_length=521, null=True, editable=True)

    class Meta:
        db_table = 'client_auth_pwd'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def save(self, *args, **kwargs):
        salt = bcrypt.gensalt(prefix=b'2b')
        if not self.password.startswith('$2b$'):
            self.password = bcrypt.hashpw(self.password.encode('utf-8'),
                                          salt).decode('utf-8')
        super().save(*args, **kwargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def check_pwd(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class TwoFA(models.Model):
    # Primary key
    key = models.CharField(primary_key=True, default=pyotp.random_base32,
                           max_length=32, null=False, editable=True)

    # Secondary key
    enable = models.BooleanField(default=False, editable=True)
    scanned = models.BooleanField(default=False, editable=True)

    class Meta:
        db_table = 'client_auth_2fa'
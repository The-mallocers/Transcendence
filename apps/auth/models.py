import uuid

import bcrypt
import pyotp
from django.db import models
from django.db.models import CharField
from django.db.models.fields import UUIDField, DateTimeField
from django.utils import timezone

from utils.enums import JWTType


class Password(models.Model):
    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)

    # Secondary key
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
    qrcode = models.ImageField(upload_to='2fa_qrcodes/', null=True, blank=True)

    def update(self, data, value) -> None:
        match data:
            case "key":
                self.key = value
            case "enable":
                self.enable = value
            case "scanned":
                self.scanned = value
            case "qrcode":
                self.qrcode = value
            case _:
                return None
        self.save()

    class Meta:
        db_table = 'client_auth_2fa'


class InvalidatedToken(models.Model):
    class Meta:
        db_table = 'auth_invalidated_tokens'

    jti = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = CharField(max_length=500, null=True)
    exp = DateTimeField()
    type = CharField(max_length=20, choices=[(jwt_type.name, jwt_type.value) for jwt_type in JWTType], null=True)

    @classmethod
    def delete_expired_token(cls):
        now = timezone.now()
        deleted, _ = cls.objects.filter(exp__lt=now).delete()
        return deleted

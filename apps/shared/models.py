import uuid

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError, transaction
from django.http import HttpRequest

from apps.profile.models import Profile
from apps.auth.models import Password, TwoFA


class Clients(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)

    #Joined tables
    password = models.ForeignKey(Password, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    twoFa = models.ForeignKey(TwoFA, on_delete=models.CASCADE)
    rights = models.ForeignKey('admin.Rights', on_delete=models.CASCADE,
                               null=True)

    class Meta:
        db_table = 'client_list'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"Client data => Email:{self.profile.email}, Username:{self.profile.username}"

    def save(self, *args, **kwargs):
        self.password.save()
        self.profile.save()
        self.twoFa.save()
        self.rights.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kargs):
        self.password.delete()
        self.profile.delete()
        self.twoFa.delete()
        self.rights.delete()
        super().delete(*args, **kargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    def get_client_by_id(id: uuid.UUID):
        if id is None:
            return None
        client = Clients.objects.get(id=id)
        return client

    @staticmethod
    def get_client_by_email(email: Profile.email):
        profile = Profile.get_profile_by_email(email)
        if profile is None:
            return None
        client = Clients.objects.filter(profile=profile).first()
        return client

    @staticmethod
    def get_client_by_request(request: HttpRequest):
        if hasattr(request, 'access_token'):
            token = request.access_token
            return Clients.get_client_by_id(token.SUB)
        return None

    @staticmethod
    def create_client(username: str, email: str, password: str):
        from apps.admin.models import Rights
        try:
            with transaction.atomic():
                if Profile.objects.filter(email=email).exists():
                    return None

                password_mod = Password(password=password)
                password_mod.save()

                profile_mod = Profile(username=username, email=email)
                profile_mod.save()

                rights_mod = Rights(is_admin=False)
                rights_mod.save()

                two_fa_mod = TwoFA()
                two_fa_mod.save()

                client = Clients(password=password_mod, profile=profile_mod,
                                 rights=rights_mod, twoFa=two_fa_mod)
                client.save()

                return client
        except IntegrityError as e:
            raise IntegrityError(f"Database integrity error: {e}")
        except ValidationError as e:
            raise ValidationError(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

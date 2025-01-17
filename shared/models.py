import uuid

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from account.models import Profile
from admin.models import Rights
from auth.models import Password


class Clients(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Joined tables
    password = models.ForeignKey(Password, on_delete=models.CASCADE, default=1)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)
    rights = models.ForeignKey(Rights, on_delete=models.CASCADE, null=True)
    # log = models.ForeignKey(Log, on_delete=models.CASCADE)

    #Funcions
    @staticmethod
    def get_client_by_id(id: uuid.UUID):
        if id is None:
            return None
        client = Clients.objects.get(id=id)
        return client

    @staticmethod
    def get_client_by_email(email: Profile.email):
        profile = Profile.get_profile(email)
        if profile is None:
            return None
        client = Clients.objects.get(profile=profile)
        return client

    @staticmethod
    def create_client(username: str, first_name: str, last_name: str,
                      email: str, password: str):
        try:
            if Profile.get_profile(email) is not None:
                raise IntegrityError(
                    f'Profile with email {email} already exist.')
            id = uuid.uuid4()

            password_mod = Password(id=id, password=password)
            password_mod.save()

            profile_mod = Profile(id=id, first_name=first_name,
                                  last_name=last_name, username=username,
                                  email=email)
            profile_mod.save()

            rights_mod = Rights(id=id, right=True)
            rights_mod.save()

            client = Clients(id=id, password=password_mod, profile=profile_mod,
                             rights=rights_mod)
            client.save()

            return client
        except IntegrityError as e:
            raise IntegrityError(f"Database integrity error: {e}")
        except ValidationError as e:
            raise ValidationError(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

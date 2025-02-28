import uuid

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError, transaction
from django.http import HttpRequest

from apps.auth.models import Password, TwoFA
from apps.player.models import Player
from apps.profile.models import Profile


class Clients(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)

    #Joined tables
    password = models.ForeignKey(Password, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    twoFa = models.ForeignKey(TwoFA, on_delete=models.CASCADE)
    rights = models.ForeignKey('admin.Rights', on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'client_list'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"Client data => Email:{self.profile.email}, Username:{self.profile.username}"

    @property
    def is_authenticated(self):
        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    def get_client_by_id(id: uuid.UUID):
        if id is None:
            return None
        client = Clients.objects.get(id=id)
        return client

    @staticmethod
    @sync_to_async
    def get_client_by_id_async(id: uuid.UUID):
        try:
            with transaction.atomic():
                return Clients.objects.get(id=id)
        except Clients.DoesNotExist:
            return None

    @staticmethod
    def get_client_by_email(email: Profile.email):
        profile = Profile.get_profile_by_email(email)
        if profile is None:
            return None
        client = Clients.objects.filter(profile=profile).first()
        return client

    @staticmethod
    def get_client_by_request(request: HttpRequest):
        from utils.jwt.JWT import JWTType
        from utils.jwt.JWTGenerator import JWTGenerator

        if 'access_token' in request.COOKIES:
            token = JWTGenerator.extract_token(request, JWTType.ACCESS)
            if not token:
                return None
            return Clients.get_client_by_id(token.SUB)

        return None

    @staticmethod
    async def get_client_by_player(player_id):
        try:
            return await Clients.objects.aget(player__id=player_id)
        except Clients.DoesNotExist:
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

                player_mod = Player(nickname=profile_mod.username)
                player_mod.save()

                client = Clients(password=password_mod, profile=profile_mod,
                                 rights=rights_mod, twoFa=two_fa_mod, player=player_mod)
                client.save()

                return client
        except IntegrityError as e:
            raise IntegrityError(f"Database integrity error: {e}")
        except ValidationError as e:
            raise ValidationError(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    @staticmethod
    @database_sync_to_async
    def exists(client_id):
        try:
            Clients.objects.get(id=client_id)
            return True
        except Clients.DoesNotExist:
            return False

    @staticmethod
    @database_sync_to_async
    def get(client_id):
        try:
            return Clients.objects.select_related('player').get(id=client_id)
        except Clients.DoesNotExist:
            return None

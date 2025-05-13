import uuid

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError, transaction
from django.http import HttpRequest

from apps.auth.models import Password, TwoFA
from apps.player.models import Player
from apps.profile.models import Profile
from utils.enums import RTables, Ranks, RanksThreshold


class Stats(models.Model):
    class Meta:
        db_table = 'client_stats'

    # ── Informations ──────────────────────────────────────────────────────────────────
    total_game = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)
    losses = models.IntegerField(default=0, blank=True)
    mmr = models.IntegerField(default=50, blank=True)
    games = models.ManyToManyField('game.Game', blank=True)


class Clients(models.Model):
    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          null=False)

    # Joined tables
    password = models.ForeignKey(Password, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL,
                                null=True)  # Changing profile deletes the old one, we change this so client doesnt get deleted.
    twoFa = models.ForeignKey(TwoFA, on_delete=models.CASCADE)
    rights = models.ForeignKey('admin.Rights', on_delete=models.CASCADE, null=True)
    stats = models.ForeignKey(Stats, on_delete=models.CASCADE, null=True)
    friend = models.ForeignKey('notifications.Friend', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'client_list'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"Client data => Email:{self.profile.email}, Username:{self.profile.username}"

    # J'overide delete pour que ca supprime tout les trucs associer quand on supprime un client
    # Hopefully it doesnt break anything else
    def delete(self, *args, **kwargs):
        self.password.delete()
        if self.profile:
            self.profile.delete()
        self.twoFa.delete()
        if self.stats:
            self.stats.delete()
        if self.friend:
            self.friend.delete()
        if self.rights:
            self.rights.delete()
        super().delete(*args, **kwargs)
        
    @property
    def is_authenticated(self):
        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    def get_id_list(clients: list['Clients']) -> list[str]:
        return [str(client.id) for client in clients]

    @staticmethod
    def get_client_by_id(client_id) -> 'Clients':
        try:
            client = Clients.objects.get(id=client_id)
            return client
        except:
            return None

    @staticmethod
    def get_client_by_username(username: str):
        try:
            return Clients.objects.get(profile__username=username)
        except:
            return None  # Or handle the error appropriately

    @staticmethod
    def get_client_by_request(request: HttpRequest):
        from utils.jwt.JWT import JWT, JWTType
        token = JWT.extract_token(request, JWTType.ACCESS)
        if token is not None:
            return Clients.get_client_by_id(token.SUB)
        return None

    @staticmethod
    @sync_to_async
    def aget_client_by_id(id: uuid.UUID):
        try:
            with transaction.atomic():
                return Clients.objects.get(id=id)
        except Clients.DoesNotExist:
            return None
        except ValidationError:
            return None

    @sync_to_async
    def aget_mmr(self):
        return self.stats.mmr

    @staticmethod
    def get_client_by_email(email: Profile.email):
        profile = Profile.get_profile_by_email(email)
        if profile is None:
            return None
        client = Clients.objects.filter(profile=profile).first()
        return client

    @staticmethod
    def get_client_by_player(player_id):
        try:
            return Clients.objects.get(player__id=player_id)
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

                player_mod = Player()
                player_mod.save()

                client_stats = Stats()
                client_stats.save()
                
                client = Clients(password=password_mod, profile=profile_mod,
                                 rights=rights_mod, twoFa=two_fa_mod, player=player_mod, stats=client_stats)
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

    @staticmethod
    def get_rank(score: int) -> str:
        # return "bronze" #While we fix this shit
        i = len(RanksThreshold)
        for rank in reversed(RanksThreshold):
            i -= 1
            if score >= rank.value:
                return list(Ranks)[i]
        return Ranks.BRONZE

    @sync_to_async
    def aget_profile_username(self):
        try:
            with transaction.atomic():
                return self.profile.username
        except Exception as e:
            raise Exception(f"Error retrieving username: {e}")

    @sync_to_async
    def get_friend_table(self):
        try:
            with transaction.atomic():
                return self.friend
        except Exception as e:
            raise Exception(f"Error retrieving friend request: {e}")

    def is_friend_by_id(self, client):
        try:
            return self.friend.friends.filter(id=client.id).exists()
        except Exception as e:
            raise Exception(f"Error retrieving client: {e}")

    def get_all_friends(self):
        try:
            friend_list = []
            for friend in self.friend.friends.all():
                friend_list.append({"client": friend,
                                    "username": friend.profile.username})
            return friend_list
        except Exception as e:
            raise Exception(f"Error retrieving client: {e}")

    def get_all_pending_request(self):
        try:
            pending_list = []
            for friend in self.friend.pending_friends.all():
                pending_list.append({"client": friend,
                                     "username": friend.profile.username})
            return pending_list
        except Exception as e:
            raise Exception(f"Error retrieving client: {e}")

    @sync_to_async
    def aget_all_pending_request(self):
        try:
            pending_list = []
            for friend in self.friend.pending_friends.all():
                pending_list.append({"client": friend,
                                     "username": friend.profile.username})
            return pending_list
        except Exception as e:
            raise Exception(f"Error retrieving client: {e}")

    @sync_to_async
    def aget_pending_request_by_client(self, target):
        try:
            for friend in self.friend.pending_friends.all():
                if friend.id == target.id:
                    return friend
            return None
        except Exception as e:
            raise Exception(f"Error retrieving target: {e}")

    @staticmethod
    async def aget_client_by_username(username: str):
        try:
            return await Clients.objects.aget(profile__username=username)
        except:
            return None

    @staticmethod
    async def aget_client_by_ID(client_id: uuid.UUID):
        try:
            return await Clients.objects.aget(id=client_id)
        except:
            return None

    @staticmethod
    async def acheck_in_queue(client, redis):
        cursor = 0
        if await redis.hget(name=RTables.HASH_G_QUEUE, key=str(client.id)):
            return RTables.HASH_G_QUEUE
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=RTables.HASH_QUEUE('*'))
            for key in keys:
                ready = await redis.hget(key, str(client.id))
                if ready and ready.decode('utf-8') == 'True':
                    return key
            if cursor == 0:
                break
        return None

    @staticmethod
    @sync_to_async
    def get_tournament_clients_infos(client_ids):
        """
        Get multiple clients with all related data in a single query
        using select_related to optimize database access
        """
        try:
            with transaction.atomic():
                # Use select_related to prefetch the related profile and stats in one query
                clients = Clients.objects.filter(id__in=client_ids).select_related('profile', 'stats')
                
                result = []
                for client in clients:
                    rank = client.get_rank(client.stats.mmr).value
                    print(f"rank is {rank}")
                    
                    info = {
                        "id": str(client.id),
                        "nickname": client.profile.username,
                        "avatar": client.profile.profile_picture.url,
                        "trophee": f'/media/rank_icon/{rank}.png',
                        "mmr": client.stats.mmr,
                    }
                    result.append(info)
                
                return result
        except Exception as e:
            raise Exception(f"Error retrieving clients info: {e}")

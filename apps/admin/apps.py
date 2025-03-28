from django.apps import AppConfig
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin'

    def ready(self):
        from apps.profile.models import Profile
        from apps.auth.models import Password
        from apps.auth.models import TwoFA
        from apps.admin.models import Rights
        from apps.shared.models import Clients
        @receiver(post_migrate)
        def create_admin_user(sender, **kwargs):
            if sender.name == self.name:
                if Clients.get_client_by_email(settings.ADMIN_EMAIL) is None:
                    with transaction.atomic():
                        print(settings.ADMIN_PWD, settings.ADMIN_USERNAME, settings.ADMIN_EMAIL)
                        profile = Profile.objects.create(email=settings.ADMIN_EMAIL, username=settings.ADMIN_USERNAME)
                        password = Password.objects.create(password=settings.ADMIN_PWD)
                        # stats = PlayerStats.objects.create()
                        # player = Player.objects.create(nickname=settings.ADMIN_USERNAME, stats=stats)
                        two_fa = TwoFA.objects.create()
                        right = Rights.objects.create(is_admin=True)
                        Clients.objects.create(profile=profile, password=password, twoFa=two_fa, rights=right)

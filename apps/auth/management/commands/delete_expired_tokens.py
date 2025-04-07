from django.core.management.base import BaseCommand

from apps.auth.models import InvalidatedToken


class Command(BaseCommand):
    help = 'Delete expired invalidated tokens from the database'

    def handle(self, *args, **kwargs):
        count = InvalidatedToken.delete_expired_token()
        if count == 0:
            return self.stdout.write(self.style.NOTICE('There is no expired tokens'))
        return self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired tokens'))

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.admin.models import Rights
from apps.auth.models import Password, TwoFA
from apps.chat.models import Rooms
from apps.client.models import Clients, Stats
from apps.notifications.models import Friend
from apps.profile.models import Profile
from utils.websockets.services.chat import uuid_global_room


class Command(BaseCommand):
    help = 'Create a test account for WebSocket testing'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the test account')
        parser.add_argument('email', type=str, help='Email for the test account')
        parser.add_argument('password', type=str, help='Password for the test account')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        existing_profile = Profile.objects.filter(email=email).first()
        if existing_profile:
            client = Clients.objects.filter(profile=existing_profile).first()
            if client:
                self.stdout.write(self.style.SUCCESS(f'{client.id}'))
                return

        try:
            with transaction.atomic():
                # Create profile
                profile = Profile.objects.create(
                    username=username,
                    email=email
                )

                # Create password
                password_obj = Password.objects.create(
                    password=password
                )

                # Create other required objects
                two_fa = TwoFA.objects.create()
                right = Rights.objects.create(is_admin=False)
                friend = Friend.objects.create()
                stats = Stats.objects.create()

                # Create client
                client = Clients.objects.create(
                    profile=profile,
                    password=password_obj,
                    twoFa=two_fa,
                    rights=right,
                    friend=friend,
                    stats=stats
                )

                # Add client to global chat room
                try:
                    global_room = Rooms.objects.get(id=uuid_global_room)
                    global_room.clients.add(client)
                except Rooms.DoesNotExist:
                    self.stdout.write(self.style.WARNING('Global chat room not found. Client not added to chat.'))

                # Output the client ID for the bash script to use
                self.stdout.write(self.style.SUCCESS(f'{client.id}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test account: {str(e)}'))
            raise

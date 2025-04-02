# Migration to create admin client

from django.db import migrations
from django.conf import settings
from django.db import transaction
from utils.websockets.services.chat import uuid_global_room

def create_admin_client(apps, schema_editor):
    # Get model classes
    Profile = apps.get_model('profile', 'Profile')
    Password = apps.get_model('authentification', 'Password')
    PlayerStats = apps.get_model('player', 'PlayerStats')
    Player = apps.get_model('player', 'Player')
    TwoFA = apps.get_model('authentification', 'TwoFA')
    Rights = apps.get_model('admin', 'Rights')
    Clients = apps.get_model('shared', 'Clients')
    Rooms = apps.get_model('chat', 'Rooms')

    # Check if admin client already exists
    existing_admin = Clients.objects.filter(profile__email=settings.ADMIN_EMAIL).first()
    
    if existing_admin is None:
        with transaction.atomic():
            # Create associated models
            profile = Profile.objects.create(
                email=settings.ADMIN_EMAIL, 
                username=settings.ADMIN_USERNAME
            )
            password = Password.objects.create(password=settings.ADMIN_PWD)
            
            player = Player.objects.create(
                nickname=settings.ADMIN_USERNAME, 
            )
            two_fa = TwoFA.objects.create()
            right = Rights.objects.create(is_admin=True)
            
            # Create admin client
            admin_client = Clients.objects.create(
                profile=profile, 
                password=password, 
                twoFa=two_fa, 
                rights=right,
                player=player
            )
            
            # Find global room
            global_room = Rooms.objects.get(id=uuid_global_room)
            
            # Set admin and add to clients
            global_room.admin = admin_client
            global_room.save()
            global_room.clients.add(admin_client)

def delete_admin_client(apps, schema_editor):
    # Clean up the admin client
    Clients = apps.get_model('shared', 'Clients')
    Rooms = apps.get_model('chat', 'Rooms')
    
    # Remove admin from global room
    try:
        global_room = Rooms.objects.get(id=uuid_global_room)
        global_room.admin = None
        global_room.save()
    except Rooms.DoesNotExist:
        pass
    
    # Delete admin client
    Clients.objects.filter(profile__email=settings.ADMIN_EMAIL).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0001_initial'),
        ('chat', '0002_create_global_chat'),  # Refer to global room migration
        ('profile', '0001_initial'),
        ('authentification', '0002_twofa_qrcode'),
        ('pong', '0001_initial'),
        ('admin', '0004_rights_grafana_dashboard'),
    ]

    operations = [
        migrations.RunPython(create_admin_client, delete_admin_client)
    ]
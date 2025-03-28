# Migration to create global chat room

from django.db import migrations
from utils.websockets.services.chat import uuid_global_room

def create_global_room(apps, schema_editor):
    Rooms = apps.get_model('chat', 'Rooms')
    
    # Check if global room already exists
    existing_room = Rooms.objects.filter(id=uuid_global_room).exists()
    
    if not existing_room:
        # Create global room
        Rooms.objects.create(
            id=uuid_global_room,
        )

def delete_global_room(apps, schema_editor):
    Rooms = apps.get_model('chat', 'Rooms')
    Rooms.objects.filter(id=uuid_global_room).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'), 
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_global_room, delete_global_room)
    ]
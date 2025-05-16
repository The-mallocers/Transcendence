from django.db import migrations
from django.db.migrations.exceptions import IrreversibleError

from utils.websockets.services.chat import uuid_global_room


def create_global_room(apps, schema_editor):
    Rooms = apps.get_model('chat', 'Rooms')
    try:
        global_room = Rooms.objects.create(id=uuid_global_room)

        Clients = apps.get_model('client', 'Clients')
        clients = Clients.objects.all()
        for client in clients:
            global_room.clients.add(client)
    except Exception as e:
        raise IrreversibleError(f'Failed to create global room: {e}')


def delete_global_room(apps, schema_editor):
    Rooms = apps.get_model('chat', 'Rooms')
    Rooms.objects.delete(id=uuid_global_room)


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0002_initial'),
        ('client', '0002_initial')
    ]

    operations = [
        migrations.RunPython(create_global_room, delete_global_room)
    ]
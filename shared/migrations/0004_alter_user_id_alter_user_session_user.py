# Generated by Django 5.1.4 on 2024-12-16 11:24

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0003_alter_user_id_alter_user_session_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('10f6b5cf-8328-4837-9787-8e60befd0a89'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='session_user',
            field=models.UUIDField(default=uuid.UUID('0ee173c9-a821-4b9b-aec0-6de0cd548d90')),
        ),
    ]
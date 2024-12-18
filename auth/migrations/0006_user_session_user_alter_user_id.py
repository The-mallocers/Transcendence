# Generated by Django 5.1.4 on 2024-12-11 14:24

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0005_alter_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='session_user',
            field=models.UUIDField(default=uuid.UUID('30bcf9b2-2f47-463c-a1fd-f6e6789b0e21')),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('9bcf25b0-e8eb-465c-a157-ad7a56a51b5e'), editable=False, primary_key=True, serialize=False),
        ),
    ]

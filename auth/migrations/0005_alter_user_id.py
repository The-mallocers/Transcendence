# Generated by Django 5.1.4 on 2024-12-09 16:11

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0004_rename_fisrt_name_user_first_name_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('80f9f357-750e-4919-b199-aa120527b0f2'), editable=False, primary_key=True, serialize=False),
        ),
    ]

# Generated by Django 5.1.4 on 2024-12-13 14:22

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('111db332-dad2-4e31-9bcc-19e16ed3fd30'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='session_user',
            field=models.UUIDField(default=uuid.UUID('7d0dd706-9621-432c-8079-b3e3813c5f0e')),
        ),
    ]
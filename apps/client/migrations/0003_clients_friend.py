# Generated by Django 5.1.7 on 2025-04-08 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('client', '0002_initial'),
        ('notifications', '0002_friend_delete_friendrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='clients',
            name='friend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='notifications.friend'),
        ),
    ]

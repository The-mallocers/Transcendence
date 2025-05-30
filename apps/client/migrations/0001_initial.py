# Generated by Django 5.1.7 on 2025-05-12 12:14

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clients',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'client_list',
            },
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_game', models.IntegerField(blank=True, default=0)),
                ('wins', models.IntegerField(blank=True, default=0)),
                ('losses', models.IntegerField(blank=True, default=0)),
                ('mmr', models.IntegerField(blank=True, default=50)),
            ],
            options={
                'db_table': 'client_stats',
            },
        ),
    ]

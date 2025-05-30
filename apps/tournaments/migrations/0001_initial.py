# Generated by Django 5.1.7 on 2025-05-12 12:14

import datetime

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.tournaments.models
import utils.util


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournaments',
            fields=[
                ('code', models.CharField(default='', editable=False, max_length=5, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('scoreboards', models.JSONField(default=list)),
                ('title', models.TextField(default="<django.db.models.fields.CharField>'s tournaments", max_length=30)),
                ('max_clients', models.IntegerField(default=8, validators=[utils.util.validate_even])),
                ('is_public', models.BooleanField(default=True)),
                ('has_bots', models.BooleanField(default=False)),
                ('timer', models.DurationField(default=datetime.timedelta(0), editable=False, null=True)),
                ('points_to_win', models.IntegerField(default=11)),
                ('clients', models.ManyToManyField(blank=True, related_name='tournaments_players', to='client.clients')),
                ('host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='host', to='client.clients')),
                ('winner',
                 models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winner', to='client.clients')),
            ],
            options={
                'db_table': 'pong_tournaments',
            },
            bases=(models.Model, apps.tournaments.models.TournamentRuntime),
        ),
    ]

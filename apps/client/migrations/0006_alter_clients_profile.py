# Generated by Django 5.1.7 on 2025-05-06 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_create_admin_squashed_0005_remove_stats_rank'),
        ('profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clients',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='profile.profile'),
        ),
    ]

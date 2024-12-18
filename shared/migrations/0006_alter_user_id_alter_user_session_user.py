# Generated by Django 5.1.4 on 2024-12-16 11:31

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0005_alter_user_id_alter_user_session_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c1123753-43b7-4ff8-bbfd-620f859bd4c2'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='session_user',
            field=models.UUIDField(default=uuid.UUID('ae1fe13c-188a-4380-aaab-963157438af7')),
        ),
    ]

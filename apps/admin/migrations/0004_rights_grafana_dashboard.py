# Generated by Django 5.1.7 on 2025-03-20 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_alter_rights_grafana_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='rights',
            name='grafana_dashboard',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]

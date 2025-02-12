import os
from celery import Celery

# Définir le fichier de configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialiser Celery
app = Celery("config")

# Charger la configuration depuis Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover des tâches dans les apps Django
app.autodiscover_tasks()
from django.db import models

# Create your models here.
class Component (models.Model):
    html = models.TextField()
    name = models.CharField(max_length=64)

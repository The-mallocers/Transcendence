import uuid

from django.db import models

# Create your models here.
class Rights(models.Model):
    #Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, null=False)

    #Secondary key
    right = models.BooleanField(default=False)

    #Functions
    def update(self, data, value):
        match data:
            case "right":
                self.right = value
            case _:
                return None
        self.save()
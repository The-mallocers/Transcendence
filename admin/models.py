from django.contrib.contenttypes.models import ContentType
from django.db import models

from shared.models import Clients


class Permission(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True, null=False, editable=False)

    # Secondary key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=False, editable=False,
                                     related_name='admin_permission_set')
    codename = models.CharField(max_length=30, null=False, editable=False)
    name = models.CharField(max_length=30, null=False, editable=False)

    def __str__(self):
        return f'{self.name} ({self.codename})'

class Rights(models.Model):
    #Primary key
    id = models.AutoField(primary_key=True, null=False, editable=False)

    #Secondary key
    is_admin = models.BooleanField(default=False, null=False, editable=True)
    permissions = models.ManyToManyField(Permission, through='RightPermission')

    def has_permission(self, codename: Permission.codename):
        return self.permissions.filter(codename=codename).exists()


class RightPermission(models.Model):
    right = models.ForeignKey(Rights, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'admin_right_permissions'

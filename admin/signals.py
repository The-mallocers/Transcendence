from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate

from admin.models import Permission


def init_permission(sender, **kwargs):
    for content_type in ContentType.objects.all():
        permissions = [
            {'codename': f'add_{content_type.model}',
             'name': f'Can add {content_type.model}'},
            {'codename': f'del_{content_type.model}',
             'name': f'Can delete {content_type.model}'},
            {'codename': f'edit_{content_type.model}',
             'name': f'Can edit {content_type.model}'},
            {'codename': f'view_{content_type.model}',
             'name': f'Can view {content_type.model}'},
        ]

        for perm in permissions:
            perm_obj, created = Permission.objects.get_or_create(
                content_type=content_type,
                codename=perm['codename'],
                defaults={'name': perm['name']}
            )


post_migrate.connect(init_permission)

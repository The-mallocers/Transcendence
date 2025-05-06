from django.http import HttpRequest
from rest_framework.permissions import BasePermission

from apps.client.models import Clients
from apps.profile.models import Profile


class ProfilePermission(BasePermission):

    def has_permission(self, request: HttpRequest, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: HttpRequest, view, obj: Profile):
        client: Clients = Clients.get_client_by_id(request.user.code)

        if client.profile_id is obj.id or client.rights.is_admin:
            return True
        else:
            return False

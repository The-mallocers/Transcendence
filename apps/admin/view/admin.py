from django.shortcuts import render

from apps.shared.models import Clients


def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        context = {
            "client": client,
            "clients": Clients.objects.all()
        }
        return render(req, "apps/admin/admin.html", context)

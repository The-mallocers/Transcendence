from django.http import HttpResponseRedirect
from django.shortcuts import render

from shared.models import Clients


def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        context = {
            "client": client,
            "clients": Clients.objects.all()
        }
        return render(req, "index.html", context)
    else:
        return HttpResponseRedirect(
            '/auth/login')  # todo il faut rediriger vers une page index mais sans le compte

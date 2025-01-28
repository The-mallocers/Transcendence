from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string

def get(request):
    client = Clients.get_client_by_request(request)
    if client is not None:
        context = {
            "client": client,
            "clients": Clients.objects.all()
        }
        return render(request, "apps/index.html", context)
    else:
        return HttpResponseRedirect('/auth/login')
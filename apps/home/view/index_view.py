from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render

from apps.shared.models import Clients


def index_view(req):
    if req.method == 'GET':
        return get(req)
    if req.method == 'POST':
        return post(req)
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not allowed"
        }, status=405)

def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        context = {
            "client": client,
            "clients": Clients.objects.all()
        }
        return render(req, "apps/index.html", context)
    else:
        return HttpResponseRedirect('/auth/login')

def post(req):
    return HttpResponse("index")
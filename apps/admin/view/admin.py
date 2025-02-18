from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

from apps.shared.models import Clients


# def get(req):
#     client = Clients.get_client_by_request(req)
#     if client is not None:
#         context = {
#             "client": client,
#             "clients": Clients.objects.all()
#         }
#         return render(req, "apps/admin/admin.html", context)


def get(request):
    client = Clients.get_client_by_request(request)
    if client is not None:
        context = {
            "client": client,
            "clients": Clients.objects.all(),
            "csrf_token": get_token(request)
        }
    html_content = render_to_string("apps/admin/admin.html", context)
    return JsonResponse({
        'html': html_content,
    })

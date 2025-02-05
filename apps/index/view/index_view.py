from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token


from apps.shared.models import Clients

def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        print("je suis la ya un client")
        context = {
            "client": client,
            "clients": Clients.objects.all()
        }
        html_content = render_to_string("apps/index.html", context)
        return JsonResponse({'html': html_content})
    else:
        print("no client detected")
        html_content = render_to_string("apps/auth/login.html", {"csrf_token": get_token(req)})
        return JsonResponse({
            'html': html_content,
        })
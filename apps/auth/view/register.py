from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

from apps.shared.models import Clients
from utils.jwt.JWTGenerator import JWTGenerator, JWTType

from django.template.loader import render_to_string
from django.middleware.csrf import get_token


def post(req: HttpRequest):
    client = Clients.get_client_by_email(req.POST.get('email'))
    if client is None:
        username = req.POST.get('username')
        email = req.POST.get('email')
        password = req.POST.get('password')
        password_check = req.POST.get('password_check')

        if password != password_check:
            return JsonResponse({
                "success": False,
                "message": "Password missmatch"
            }, status=400)

        client = Clients.create_client(username, email, password)
        response = JsonResponse({
            "success": True,
            "message": "Register successful"
        }, status=200)
        JWTGenerator(client, JWTType.ACCESS).set_cookie(response=response)
        JWTGenerator(client, JWTType.REFRESH).set_cookie(response=response)
        return response
    else:
        return JsonResponse({
            "success": False,
            "message": "Account already exist"
        }, status=400)


def get(req):
    print("in the register get view!")
    html_content = render_to_string("apps/auth/register.html", {"csrf_token": get_token(req)})
    return JsonResponse({
        'html': html_content,
    })
    # users = Clients.objects.all()
    # context = {"users": users}
    # return render(req, "apps/auth/register.html", context)

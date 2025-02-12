from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

from apps.shared.models import Clients
from utils.jwt.JWTGenerator import JWTGenerator, JWTType
from django.template.loader import render_to_string
from django.middleware.csrf import get_token



def post(req: HttpRequest):
    email = req.POST.get('email')
    password = req.POST.get("password")
    client = Clients.get_client_by_email(email)

    if all(v is None for v in [email, password]):
        return JsonResponse({
            "success": False,
            "message": "Invalid post request"
        }, status=400)

    if client is None:
        return JsonResponse({
            "success": False,
            "message": "Wrong credentials"
        }, status=401)

    if client.password.check_pwd(password):
        response = JsonResponse({
            "success": True,
            "message": "You've been correctly login"
        }, status=200)
        JWTGenerator(client, JWTType.ACCESS).set_cookie(
            response=response)
        JWTGenerator(client, JWTType.REFRESH).set_cookie(
            response=response)
        return response
    else:
        return JsonResponse({
            "success": False,
            "message": "Wrong credentials"
        }, status=401)

def get(req):
    users = Clients.objects.all()
    # Get the CSRF token
    csrf_token = get_token(req)
    
    # Render the HTML template to a string
    html_content = render_to_string("apps/auth/login.html", {"users": users, "csrf_token": csrf_token})
    
    # Return both the HTML and any additional data
    return JsonResponse({
        'html': html_content,
        'users': list(users.values())
    })
    # users = Clients.objects.all()

    # context = {"users": users}

    # return render(req, "apps/auth/login.html", context)
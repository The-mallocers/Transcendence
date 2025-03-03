from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

from apps.shared.models import Clients
from utils.jwt.JWTGenerator import JWTGenerator, JWTType

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os

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
            "message": "You've been corectlly login"
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
    print("ta mere")
    # url = render_dashboard(req);
    users = Clients.objects.all()

    context = {"users": users}

    return render(req, "apps/auth/login.html", context)

# For an API endpoint that returns JSON directly:
# def render_dashboard(request) -> str:
#     secretkey = os.environ.get('GRAFANA_BEARERKEY')
#     print(secretkey)
#     api_url = "http://grafana:3000/api/search?type=dash-db"
    
#     my_headers = {
#         'Accept': 'application/json',
#         "Content-Type": "application/json",
#     "Authorization": f'Bearer {secretkey}'
#     }
#     try:
#         response = requests.get(
#             api_url,
#             params=request.GET.dict(),  # Pass along all query parameters
#             headers=my_headers
#         )
#         response.raise_for_status()
#         data = response.json()
#         print(data)
#         url = data[0].get('url')
#         return url
    
#     except requests.exceptions.RequestException as e:
#         print(str(e))
#         return JsonResponse({'error': str(e)}, status=500)

from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

from apps.shared.models import Clients
from utils.jwt.JWTGenerator import JWTGenerator, JWTType

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

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
    users = Clients.objects.all()

    api_proxy(req);
    context = {"users": users}

    return render(req, "apps/auth/login.html", context)

def fetch_api_data(request):
    api_url = "http://localhost:3000"  # Replace with your actual API URL
    
    # You can add parameters from the request
    params = {}
    if request.GET.get('query'):
        params['q'] = request.GET.get('query')
    
    # Add headers if needed (e.g., for authentication)
    headers = {
        # 'Authorization': f'Bearer {settings.API_KEY}',
        # 'Content-Type': 'application/json'
        'Accept': 'application/json',
        "Content-Type": "application/json",
       "Authorization": 'Bearer {settings.GRAFANA_BEARERKEY}'
    }
    
    try:
        # Make the API request
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse the response
        data = response.json()
        
        # Return the data to the template
        return render(request, 'api_data.html', {'data': data})
    
    except requests.exceptions.RequestException as e:
        # Handle any errors
        return JsonResponse({'error': str(e)}, status=500)

# For an API endpoint that returns JSON directly:
def api_proxy(request):
    api_url = "http://localhost:3000/api/search?type=dash-db"
    
    my_headers = {
        'Accept': 'application/json',
        "Content-Type": "application/json",
       "Authorization": 'Bearer {settings.GRAFANA_BEARERKEY}'
    }
    try:
        response = requests.get(
            api_url,
            params=request.GET.dict(),  # Pass along all query parameters
            headers=my_headers
        )
        response.raise_for_status()
        print(response.json())
        # return JsonResponse(response.json())
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
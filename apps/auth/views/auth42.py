
# import requests
# from rest_framework import status

# from django.conf import settings
# from django.contrib.auth import login
# from django.shortcuts import redirect
# from django.http import HttpResponse, JsonResponse

# from rest_framework.response import Response

# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.models import User
# import json

# from apps.auth.api.views import formulate_json_response, get_qrcode
# from apps.shared.api.serializers import ClientSerializer
# from apps.shared.models import Clients
# from utils.jwt.JWT import JWTType
# from utils.jwt.JWTGenerator import JWTGenerator


# def auth42(request):
#     # Existing token exchange logic remains the same
#     # This view now handles both the redirect and token exchange
#     # Extract authorization code from the GET parameters
#     print("meow")
#     auth_code = request.GET.get('code')
#     print("lalalalalala", auth_code)
#     token_params = {
#         'grant_type': 'authorization_code',
#         'client_id': 'u-s4t2ud-fba0f059cba0019f374c8bf89cb3a81ead9ef0cb218380d9344c21d99d1f9b3e',
#         'client_secret': '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',
#         'code': auth_code,
#         'redirect_uri': 'https://localhost:8000/auth/auth42'
#     }
    
#     # Exchange code for access token
#     token_response = requests.post(
#         'https://api.intra.42.fr/oauth/token', 
#         json=token_params
#     )

#     print(token_response)
#     token_data = token_response.json()
#     access_token = token_data.get('access_token')
#     print(access_token)
#     user_response = requests.get(
#         'https://api.intra.42.fr/v2/me',
#         headers={'Authorization': f'Bearer {access_token}'}
#     )
#     # Extract relevant user information
#     user_data = user_response.json()
#     email = user_data.get('email')
#     username = user_data.get('login')

#     # Check if user exists or create
#     client = Clients.get_client_by_email(email)
#     if not client:
#         client = Clients.create_client(username, email, "Matboyer@42")


#     # Create JWT tokens
#     response = formulate_json_response(True, 302, "Login Successful", "/")
    
#     JWTGenerator(client, JWTType.ACCESS).set_cookie(response)
#     JWTGenerator(client, JWTType.REFRESH).set_cookie(response)

#     return response

import requests
from rest_framework import status

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse

from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from apps.auth.api.views import formulate_json_response, get_qrcode
# from apps.shared.api.serializers import ClientSerializer
# from apps.shared.models import Clients
from apps.client.models import Clients
from utils.jwt.JWT import JWTType
from utils.jwt.JWT import JWT

from django.db.migrations.exceptions import IrreversibleError
from utils.util import format_validation_errors

from utils.serializers.client import ClientSerializer


def auth42(request):
    # Existing token exchange logic remains the same
    # This view now handles both the redirect and token exchange
    # Extract authorization code from the GET parameters

    auth_code = request.GET.get('code')
    print("lalalalalala", auth_code)
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': 'u-s4t2ud-fba0f059cba0019f374c8bf89cb3a81ead9ef0cb218380d9344c21d99d1f9b3e',
        'client_secret': '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',
        'code': auth_code,
        'redirect_uri': 'https://localhost:8000/auth/auth42'
    }
    
    # Exchange code for access token
    token_response = requests.post(
        'https://api.intra.42.fr/oauth/token', 
        json=token_params
    )

    print(token_response)
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    print(access_token)
    user_response = requests.get(
        'https://api.intra.42.fr/v2/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    # Extract relevant user information
    user_data = user_response.json()
    email = user_data.get('email')
    username = user_data.get('login')

    # Check if user exists or create
    client = Clients.get_client_by_email(email)

    print(username, client)
    if not client and email and username:
        data = {
            'profile': {
                'first_name': username,
                'last_name': '42',
                'email': email,
                'username': username
            },
            'password': {
                'password': "Matboyer@42",
                'passwordcheck': "Matboyer@42"
            }
        }
        serializer = ClientSerializer(data=data, context={'is_admin': False})
        if serializer.is_valid():
            serializer.save()
        else:
            raise IrreversibleError(f'Failed to create admin in migration file: '
                                    f'{format_validation_errors(serializer.errors)}')
        

        # client = Clients.create_client(username, email, "Matboyer@42")


    # # Create JWT tokens
    response = formulate_json_response(True, 302, "Login Successful", "/")
    
    JWT(serializer, JWTType.ACCESS).set_cookie(response)
    JWT(serializer, JWTType.REFRESH).set_cookie(response)

    return response

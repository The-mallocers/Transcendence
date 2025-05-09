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
from django.conf import settings
import os

import random
import string


from django.template.loader import render_to_string
from django.middleware.csrf import get_token


def generate_password():
    length = random.randint(8, 32)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# print(generate_password())


def auth42(request):
    auth_code = request.GET.get('code')
    print("lalalalalala", auth_code)
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': os.environ.get('AUTH_42_CLIENT'),
        'client_secret':  os.environ.get('AUTH_42_SECRET'),
        'code': auth_code,
        'redirect_uri': 'https://localhost:8000/auth/auth42'
    }
    
    token_response = requests.post(
        'https://api.intra.42.fr/oauth/token', 
        json=token_params
    )

    print(token_response)
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    print("acess token")
    print(access_token)
    user_response = requests.get(
        'https://api.intra.42.fr/v2/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_data = user_response.json()
    email = user_data.get('email')
    username = user_data.get('login')

    client = Clients.get_client_by_email(email)

    print(username, client)

    serializer = None
    if not client:
        generated_pwd = generate_password()
        data = {
            'profile': {
                'first_name': username,
                'last_name': 'test',
                'email': email,
                'username': username
            },
            'password': {
                'password': generated_pwd,
                'passwordcheck': generated_pwd,
            }
        }
        serializer = ClientSerializer(data=data, context={'is_admin': False})
        if serializer.is_valid():
            client = serializer.save()
        else:
            raise IrreversibleError(f'Failed to create admin in migration file: '
                                    f'{format_validation_errors(serializer.errors)}')


    # csrf_token = get_token(request)


    # html_content = render_to_string("apps/auth/42fallback.html", {
    #     "csrf_token": csrf_token,
    # })

    # response = JsonResponse({
    #     'html': html_content,
    # })

    # response = formulate_json_response(True, 200, "Login Successful", "/")
    response = formulate_json_response(True, 302, "Login Successful", "/")

    response.set_cookie("oauthToken", access_token)
    JWT(client, JWTType.ACCESS).set_cookie(response)
    JWT(client, JWTType.REFRESH).set_cookie(response)

    return response

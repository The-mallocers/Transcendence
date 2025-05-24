import os
import random
import string

import requests

from apps.auth.api.views import formulate_json_response
# from apps.shared.api.serializers import ClientSerializer
# from apps.shared.models import Clients
from apps.client.models import Clients
from config import settings
from utils.jwt.JWT import JWT
from utils.jwt.JWT import JWTType
from utils.serializers.client import ClientSerializer
from apps.auth.api.views import isClientOnline
from asgiref.sync import async_to_sync


def generate_password():
    length = random.randint(8, 32)
    characters = string.ascii_letters + string.digits + string.punctuation.replace('$', '')
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def add_suffix_until_unique(username):
    i = 1
    username = username + str(i)
    while (Clients.get_client_by_username(username) is not None):
        username = username[:-len(str(i))]
        username = username + str(i)
        i += 1
    return username


def auth42(request):
    try : 
        auth_code = request.GET.get('code')
        print('code :', auth_code)
        hostname = request.get_host().split(':')[0]
        print('host :', hostname)
        token_params = {
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('AUTH_42_CLIENT'),
            'client_secret': os.environ.get('AUTH_42_SECRET'),
            'code': auth_code,
            'redirect_uri': f'https://{hostname}:8000/auth/auth42'
        }
        print('token params :', token_params)
        token_response = requests.post(
            'https://api.intra.42.fr/oauth/token',
            json=token_params
        )
        print('token response :', token_response)
        print('response code :', token_response.status_code)
        if token_response.status_code != 200:
            response = formulate_json_response(True, 302, "Login Unsuccessful", "/")
            return response
        token_data = token_response.json()
        print('token data :', token_data)
        access_token = token_data.get('access_token')
        print('access_token :', access_token)
        user_response = requests.get(
            'https://api.intra.42.fr/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if (user_response.status_code != 200):
            print("MWHAHAHA JE T'AI EU ERREUR DE MIERDA (1)")
        print('access_token :', user_response, "user_response_code", user_response.status_code)
        user_data = user_response.json()
        print('user_data :', user_data)


        id = user_data.get('id')
        email = user_data.get('email')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        username = user_data.get('login')
        if (Clients.get_client_by_username(username) is not None):
            username = add_suffix_until_unique(username)

        # GET /v2/users/:user_id/coalitions
        coa_response = requests.get(
            f'https://api.intra.42.fr/v2/users/{id}/coalitions',
            headers={'Authorization': f'Bearer {access_token}'})

        if (coa_response.status_code != 200):
            print("MWHAHAHA JE T'AI EU ERREUR DE MIERDA (1)")
        coa_data = coa_response.json()
        coa = coa_data[0].get('name')
        client = Clients.get_client_by_email(email)

        serializer = None
        if client:
            isOnline = async_to_sync(isClientOnline)(client)
            if isOnline:
                return formulate_json_response(False, 401, "You are already logged in somewhere else", "/")
        
        if not client:
            generated_pwd = generate_password()
            data = {
                'profile': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'username': username,
                    'coalition': coa
                },
                'password': {
                    'password': generated_pwd,
                    'passwordcheck': generated_pwd,
                }
            }

            serializer = ClientSerializer(data=data, context={'is_admin': False})

            if serializer.is_valid():
                client = serializer.save()
        
        response = formulate_json_response(True, 302, "Login Successful", "/")

        # response.set_cookie("oauthToken", access_token)
        JWT(client, JWTType.ACCESS, request).set_cookie(response)
        JWT(client, JWTType.REFRESH, request).set_cookie(response)

        return response
    except :
        return formulate_json_response(False, 302, "There was an error while trying to comunicate to 42 api , please try again", "/")
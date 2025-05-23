import random

# from django.forms import ValidationError
from rest_framework.exceptions import ValidationError

from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.models import Password
from apps.client.models import Clients
from apps.profile.models import Profile
from apps.auth.models import TwoFA
from utils import serializers
from utils.enums import JWTType, RTables
from utils.jwt.JWT import JWT
from utils.redis import RedisConnectionPool
from utils.serializers.auth import PasswordSerializer
from utils.serializers.client import ClientSerializer
from utils.serializers.permissions.auth import PasswordPermission
from utils.serializers.picture import ProfilePictureValidator
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync

class PasswordApiView(APIView):
    permission_classes = [PasswordPermission]

    def get_object(self, pk):
        try:
            return Password.objects.get(id=pk)
        except Password.DoesNotExist:
            return None

    def patch(self, request, pk, *args, **kwargs):
        password_instance = self.get_object(pk)
        self.check_object_permissions(self.request, password_instance)

        if not password_instance:
            return Response({"password": ["Password entry not found."]}, status=status.HTTP_404_NOT_FOUND)

        serializer = PasswordSerializer(password_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"password": {"valid": True, "id": serializer.data.get('id')}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        options = ["Fire", "Earth", "Water", "Air"]
        coa = random.choice(options)
        request.data['profile']['coalition'] = coa
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = serializer.save()  # this can fail so we added a catch
                
                print("client: ", client)
                logger.info(f'Client create successfully: {client}')
                response = Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
                JWT(client, JWTType.ACCESS, request).set_cookie(response)  # vous aviez raison la team c'est mieux
                JWT(client, JWTType.REFRESH, request).set_cookie(response)
                return response
            except Exception as e:
                import traceback
                logging.getLogger('MainThread').error(traceback.format_exc())
                return Response({"error": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logging.getLogger('MainThread').error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateApiView(APIView):
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            # We get rid of the empty fields
            for section in list(data.keys()):
                if isinstance(data[section], dict):
                    for key in list(data[section].keys()):
                        if data[section][key] == "":
                            del data[section][key]
                    if not data[section]:
                        del data[section]

            client = Clients.get_client_by_request(request)
            serializer = ClientSerializer(instance=client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # HANDLE EMAIL CASE
                # IF A NEW EMAIL WAS GIVEN, IT MEANS WE ACTUALLY CREATED A NEW PROFILE.
                if 'profile' in data and 'email' in data['profile']:
                    old_email = client.profile.email
                    new_email = data['profile']['email']
                    client.profile = Profile.objects.filter(email=new_email).first()
                    Profile.objects.filter(email=old_email).delete()
                    client.save()
                # else, we return ou profile that was updated naturally.
                return Response({"message": "Infos updated succesfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (ValidationError) as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class LoginApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        email = request.POST.get('email')
        pwd = request.POST.get('password')
        client = Clients.get_client_by_email(email)
        if client is None or client.password.check_pwd(password=pwd) is False:
            return Response({
                "error": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = None
            isOnline = async_to_sync(isClientOnline)(client)
            if isOnline:
                return Response({
                "error": "You are already logged in somewhere else"
            }, status=status.HTTP_401_UNAUTHORIZED)
            # adding the 2fa check here
            elif client.twoFa.enable:
                if not client.twoFa.scanned:
                    get_qrcode(client, False)
                response = Response({
                    'message': '2FA activated, redirecting',
                    'redirect': '/auth/2fa',
                }, status=status.HTTP_302_FOUND)
                response.set_cookie(key='email', value=email, httponly=False, secure=True,
                                    samesite='Lax')  # httpfalse is less ugly than the alternatives

            else:
                response = Response({
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
                JWT(client, JWTType.ACCESS, request).set_cookie(response)
                JWT(client, JWTType.REFRESH, request).set_cookie(response)
            return response
    


# TODO, add the fact that we disconnect the notif socket/Get rid of the client in redis
class LogoutApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.COOKIES.get('access_token') is not None:
            response = Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            response.delete_cookie('oauthToken')
            try:
                JWT.extract_token(request, JWTType.REFRESH).invalidate_token()
            except Exception as e:
                logging.getLogger('MainThread').error("Couldnt invalidate the token, it was probably either deleted or modified")
                logging.getLogger('MainThread').error(str(e))
            return response
        else:
            return Response({
                "error": "You are not logged in"
            }, status=status.HTTP_401_UNAUTHORIZED)


from django.http import JsonResponse
import json


# the 2FA does not use the restful api stuff like above, too bad !
def change_two_fa(req):
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        client = Clients.get_client_by_request(req)
        if client is not None:
            if(data['status']):
                if get_qrcode(client, True) == True:
                    response = JsonResponse({
                        "success": True,
                        "state": True,
                        "image": client.twoFa.qrcode.url,
                        "message": "State 2fa change to true",
                    }, status=200)
            else:
                client.twoFa.update("enable", False)
                response = JsonResponse({
                    "success": True,
                    "state": False,
                    "message": "State 2fa change to false"
                }, status=200)
        else:
            response = JsonResponse({
                "success": False,
                "message": "No user match this request"
            }, status=404)
        return response

import pyotp
import qrcode
import io
from django.core.files.base import ContentFile


def get_qrcode(user, binary):
    if not user.twoFa.qrcode or binary is True:
        old_twofa = user.twoFa
        
        new_key = pyotp.random_base32()
        new_twofa = TwoFA(
            key=new_key,
            enable=False,
            scanned=False
        )
        new_twofa.save()
        
        user.twoFa = new_twofa
        user.save()
        
        uri = pyotp.totp.TOTP(new_key).provisioning_uri(
            name=user.profile.username,
            issuer_name="Transcendance_" + str(user.profile.username)
        )
        
        qr_image = qrcode.make(uri)
        buf = io.BytesIO()
        qr_image.save(buf, "PNG")
        contents = buf.getvalue()
        
        image_file = ContentFile(contents, name=f"{user.profile.username}_qrcode.png")
        new_twofa.qrcode = image_file
        new_twofa.save()
        # Delete old TwoFA if not used by any other client
        if old_twofa and Clients.objects.filter(twoFa=old_twofa).count() <= 1:
            if old_twofa.qrcode:
                old_twofa.qrcode.delete(save=False)
            old_twofa.delete()
            
        return True
    return False

def post_check_qrcode(req):
    client = Clients.get_client_by_request(req)
    if client: 
        if req.method == "POST":
            data = json.loads(req.body.decode('utf-8'))
            totp = pyotp.TOTP(client.twoFa.key)
            is_valid = totp.verify(data['code'])
            if is_valid:
                client.twoFa.update("enable", True)
                if not client.twoFa.scanned:
                    client.twoFa.update("scanned", True)
                response = formulate_json_response(True, 200, "2Fa successfully activate", "/profile/settings") 
                return response
            else:
                return formulate_json_response(False, 200, "Invalid code", "/profile/settings")
        else:
            return formulate_json_response(False, 405, "Method not allowed for this request", "/profile/settings")    
    else:
        return formulate_json_response(False, 404, "No user match this request", "/profile/settings")

def post_twofa_code(req):
    email = req.COOKIES.get('email')
    client = Clients.get_client_by_email(email)
    if client is None:
        return formulate_json_response(False, 404, "No user match this request", "/auth/login")
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        totp = pyotp.TOTP(client.twoFa.key)
        is_valid = totp.verify(data['code'])
        if is_valid:
            if not client.twoFa.scanned:
                client.twoFa.update("scanned", True)
            response = formulate_json_response(True, 200, "Login Successful", "/")
            JWT(client, JWTType.ACCESS, req).set_cookie(response)
            JWT(client, JWTType.REFRESH, req).set_cookie(response)
            return response
        else:
            response = formulate_json_response(False, 200, "Invalid Code", "/auth/login")
    else:
        response = formulate_json_response(False, 401, "Method not allowed for this request", "/auth/login")
    return response

def formulate_json_response(state, status, message, redirect):
    return (JsonResponse({
        "success": state,
        "message": message,
        "redirect": redirect
    }, status=status))

import logging

logger = logging.getLogger(__name__)


class GetClientIDApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        logger.debug("Trying to get client")
        client = Clients.get_client_by_request(request)
        if client == None:
            return Response({
                "client_id": None,
                "message": "Could not retrieve user ID"
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            "client_id": client.id,
            "message": "ID retrieved succesfully"
        }, status=status.HTTP_200_OK)


class UploadPictureApiView(APIView):
    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            client = Clients.get_client_by_request(request)
            profile = client.profile

            if not profile:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = ProfilePictureValidator(data=request.data)

            if serializer.is_valid():
                profile.profile_picture = serializer.validated_data['profile_picture']
                profile.save()
                return Response({"message": "Profile picture updated successfully",
                                 "picture": profile.profile_picture.url}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Maybe later add the check to see if the player is in a tournament or something.
# This code essentially logs out THEN delete the account.

class DeleteApiView(APIView):
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.COOKIES.get('access_token') is not None:
            response = Response({"message": "Successfully deleted your account."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            response.delete_cookie('oauthToken')
            try:
                JWT.extract_token(request, JWTType.REFRESH).invalidate_token()
            except Exception as e:
                logging.getLogger('MainThread').error(str(e))
            

            redis = RedisConnectionPool.get_sync_connection('api')
            client = Clients.get_client_by_request(request)
            if (redis.hexists(RTables.HASH_MATCHES, str(client.id))):
                return Response({
                    "error": "You are currently in a match, please leave it before deleting your account"
                }, status=status.HTTP_401_UNAUTHORIZED)
            for key in redis.scan_iter(RTables.HASH_TOURNAMENT_QUEUE('*')):
                if redis.hexists(key, str(client.id)):
                    return Response({
                        "error": "You are currently in a tournament, please end it before deleting your account"
                    }, status=status.HTTP_401_UNAUTHORIZED)
            client.delete()
            RedisConnectionPool.close_sync_connection('api')
            return response
        else:
            return Response({
                "error": "You are not logged in"
            }, status=status.HTTP_401_UNAUTHORIZED)


async def isClientOnline(client):
    redis = await RedisConnectionPool.get_async_connection("is_client_online")
    client_keys = await redis.keys("client_*")
    # Decode because this gets us the results in bytes
    if client_keys and isinstance(client_keys[0], bytes):
        client_keys = [key.decode() for key in client_keys]
    client_ids = [key.removeprefix("client_") for key in client_keys]
    if str(client.id) in client_ids:
        return True
    else:
        return False

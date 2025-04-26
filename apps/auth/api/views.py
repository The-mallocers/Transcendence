from django.forms import ValidationError
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.models import Password
from apps.client.models import Clients
from apps.profile.models import Profile
from utils.enums import JWTType
from utils.jwt.JWT import JWT
from utils.serializers.auth import PasswordSerializer
from utils.serializers.client import ClientSerializer
from utils.serializers.permissions.auth import PasswordPermission
from utils.serializers.picture import ProfilePictureValidator



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
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = serializer.save()  # this can fail so we added a catch
                logger.info(f'Client create successfully: {client}')
                return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                import traceback
                print("\n\nException during save:", str(e))
                logging.getLogger('MainThread').error(traceback.format_exc())
                return Response({"error": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# const data = {
#     profile: {
#         username: username,
#         email: email
#     },
#     password: {
#         password: password,
#         passwordcheck: passwordcheck
#     }
# }

class UpdateApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            for section in list(data.keys()):
                if isinstance(data[section], dict):
                    for key in list(data[section].keys()):
                        if data[section][key] == "":
                            del data[section][key]
                    if not data[section]:
                        del data[section]   

            print("data:", data)
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
                #else, we return ou profile that was updated naturally.
                return Response({"message": "Infos updated succesfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        except ValidationError as e:
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
            # adding the 2fa check here
            if client.twoFa.enable:
                if not client.twoFa.scanned:
                    get_qrcode(client)
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
                JWT(client, JWTType.ACCESS).set_cookie(response)
                JWT(client, JWTType.REFRESH).set_cookie(response)
            return response


class LogoutApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.COOKIES.get('access_token') is not None:
            response = Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        else:
            return Response({
                "error": "You are not log"
            }, status=status.HTTP_401_UNAUTHORIZED)


from django.http import JsonResponse
import json


# the 2FA does not use the restful api stuff like above, too bad !
def change_two_fa(req):
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        client = Clients.get_client_by_request(req)
        if client is not None:
            client.twoFa.update("enable", data['status'])
            response = JsonResponse({
                "success": True,
                "message": "State 2fa change"
            }, status=200)
        else:
            response = JsonResponse({
                "success": False,
                "message": "No client available"
            }, status=403)
        return response


# utils function for 2fa
import pyotp
import qrcode
import io
from django.core.files.base import ContentFile


def get_qrcode(user):
    # create a qrcode and convert it
    print("first_name: " + user.profile.username + " creating qrcode")
    if not user.twoFa.qrcode:
        uri = pyotp.totp.TOTP(user.twoFa.key).provisioning_uri(name=user.profile.username,
                                                               issuer_name="Transcendance_" + str(
                                                                   user.profile.username))
        qr_image = qrcode.make(uri)
        buf = io.BytesIO()
        qr_image.save(buf, "PNG")
        contents = buf.getvalue()

        # convert it to adapt to a imagefield type in my db
        image_file = ContentFile(contents, name=f"{user.profile.username}_qrcode.png")
        user.twoFa.update("qrcode", image_file)

        return True
    return False


def formulate_json_response(state, status, message, redirect):
    return (JsonResponse({
        "success": state,
        "message": message,
        "redirect": redirect
    }, status=status))


def post_twofa_code(req):
    email = req.COOKIES.get('email')
    client = Clients.get_client_by_email(email)
    response = formulate_json_response(False,    400, "Error getting the user", "/auth/login")
    if client is None:
        return response
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        totp = pyotp.TOTP(client.twoFa.key)
        is_valid = totp.verify(data['code'])
        if is_valid:
            if not client.twoFa.scanned:
                client.twoFa.update("scanned", True)
            response = formulate_json_response(True, 200, "Login Successful", "/")
            JWT(client, JWTType.ACCESS).set_cookie(response)
            JWT(client, JWTType.REFRESH).set_cookie(response)
            return response
    response = formulate_json_response(False, 400, "No email match this request", "/auth/login")
    return response


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
        print("Its getting here !")
        try:
            client = Clients.get_client_by_request(request)
            profile = client.profile

            if not profile:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = ProfilePictureValidator(data=request.data)

            if serializer.is_valid():
                profile.profile_picture = serializer.validated_data['profile_picture']
                profile.save()
                return Response({"message": "Profile picture updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

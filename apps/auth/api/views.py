from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.api.permissions import PasswordPermission
from apps.auth.api.serializers import PasswordSerializer
from apps.auth.models import Password
from apps.shared.api.serializers import ClientSerializer
from apps.shared.models import Clients
from utils.jwt.JWT import JWTType
from utils.jwt.JWTGenerator import JWTGenerator


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
                client = serializer.save() #this can fail so we added a catch
                print("\n\nSave successful!\n\n")
                return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                import traceback
                print("\n\nException during save:", str(e))
                print(traceback.format_exc())
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) #this is ia stuff, maybe shouldnt be 500 idk
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            #adding the 2fa check here
            if client.twoFa.enable:
                if not client.twoFa.scanned:
                    get_qrcode(client)
                response = Response({
                    'message': '2FA activated, redirecting',
                    'redirect': '/auth/2fa',
                }, status=status.HTTP_302_FOUND)
                response.set_cookie(key='email', value=email, httponly=False, secure=True, samesite='Lax') #httpfalse is less ugly than the alternatives
                
            else:
                response = Response({
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
                JWTGenerator(client, JWTType.ACCESS).set_cookie(response)
                JWTGenerator(client, JWTType.REFRESH).set_cookie(response)
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

#the 2FA does not use the restful api stuff like above, too bad !
def change_two_fa(req):
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        client = Clients.get_client_by_request(req)
        if client is not None :
            client.twoFa.update("enable", data['status'])
            response = JsonResponse({
                "success" : True,
                "message" : "State 2fa change"
            }, status=200)
        else :
            response = JsonResponse({
            "success" : False,
            "message" : "No client available"
        }, status=403)
        return response
    
#utils function for 2fa
import pyotp
import qrcode
import io
from django.core.files.base import ContentFile

def get_qrcode(user):
    # create a qrcode and convert it
    print("first_name: " + user.profile.username + " creating qrcode")
    if not user.twoFa.qrcode:
        uri = pyotp.totp.TOTP(user.twoFa.key).provisioning_uri(name=user.profile.username, issuer_name="Transcendance_" + str(user.profile.username))
        qr_image = qrcode.make(uri)
        buf = io.BytesIO()
        qr_image.save(buf, "PNG")
        contents = buf.getvalue()
        
        # convert it to adapt to a imagefield type in my db
        image_file = ContentFile(contents, name=f"{user.profile.username}_qrcode.png")
        user.twoFa.update("qrcode", image_file)
        
        return True
    return False

def formulate_json_response(state,status, message, redirect):
    return(JsonResponse({
            "success": state,
            "message": message,
            "redirect":redirect
        }, status=status))

def post_twofa_code(req):
    email = req.COOKIES.get('email')
    client = Clients.get_client_by_email(email)
    response = formulate_json_response(False, 400, "Error getting the user", "/auth/login") 
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
            JWTGenerator(client, JWTType.ACCESS).set_cookie(
                response=response)
            JWTGenerator(client, JWTType.REFRESH).set_cookie(
                response=response)
            return response
    response = formulate_json_response(False, 400, "No email match this request", "/auth/login")
    return response


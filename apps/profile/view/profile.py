from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render

from apps.profile.models import Profile
from apps.shared.models import Clients


def get(req, client_id=None):
    if client_id is not None:
        client = Clients.get_client_by_id(client_id)
    else:
        client = Clients.get_client_by_request(req)
    if client is not None:
        context = {"client": client}
        return render(req, "account/account.html", context)
    else:
        return HttpResponseRedirect(
            '/auth/login')  # todo il faut afficher une erreur sur le html au lieu de rediriger vers login


def post(request: HttpRequest, client_id):
    client = Clients.get_client_by_id(client_id)
    if client is not None:
        profile: Profile = client.profile
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        picture = request.FILES.get('profile_picture')
        password = request.POST.get('password')

        if email is not None:
            profile.email = email
        if username is not None:
            profile.username = username
        if first_name is not None:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if picture is not None:
            profile.profile_picture = picture
        if len(password):
            client.password.password = password
        try:
            client.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            }, status=200)
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Client not found.'
        })


def delete(request, client_id):
    client = Clients.get_client_by_id(client_id)
    if client is not None:
        client.delete()
        return JsonResponse({
            'success': True,
            'message': "Account has been deleted"
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Account not found'
        }, status=404)
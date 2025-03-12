from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

from apps.profile.models import Profile
from apps.shared.models import Clients


def get(req):
    requestUsername = req.GET.get("username", "minimeow")
    client = Clients.get_client_by_username(requestUsername)
    print(requestUsername, client)
    # do something if client not found

    if client is None : 
        html_content = render_to_string("apps/error/404.html", {"csrf_token": get_token(req), "error_code": "404"})
        return JsonResponse({
            'html': html_content,
        })
     
    html_content = render_to_string("apps/profile/profile.html", {"csrf_token": get_token(req), "client": client})
    return JsonResponse({
        'html': html_content,
    })
    
def get_settings(req):
    html_content = render_to_string("apps/profile/myinformations.html", {"csrf_token": get_token(req)})
    return JsonResponse({
        'html': html_content,
    })

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
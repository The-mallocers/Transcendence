import json

from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render

from account.models import Profile
from shared.models import Clients


def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        context = {"client": client}
        return render(req, "account/account.html", context)
    else:
        return HttpResponseRedirect('/auth/login')


def post(request: HttpRequest):
    client = Clients.get_client_by_request(request)
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
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Client not found.'
        })

def put(request):
    return JsonResponse({})


def delete(request):
    client = Clients.get_client_by_request(request)
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

def patch(request):
    client = Clients.get_client(request)
    try:
        body = json.loads(request.body)
        data = body.get('data')
        value = body.get('value')
        if client.update(data, value) is None:
            return JsonResponse({
                "success": False,
                "message": "Client update failed"
            }, status=401)
        else:
            return JsonResponse({
                "success": True,
                "message": "Client update"
            }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid json format"
        }, status= 401)
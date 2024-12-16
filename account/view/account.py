import json

from django.http import JsonResponse
from django.shortcuts import render

from shared.models import User

def account_view(request):
    if request.method == 'GET':
        return get(request)
    if request.method == 'POST':
        return post(request)
    if request.method == 'PUT':
        return put(request)
    if request.method == 'PATCH':
        return patch(request)
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not allowed"
        }, status=405)

def get(request):
    user = User.get_user(request)
    context = {"user": user}
    return render(request, "account/account.html", context)

def post(request):
    return JsonResponse({
        "success": False,
        "message": "Method not allowed"
    }, status=405)

def put(request):
    return JsonResponse({})

def patch(request):
    user = User.get_user(request)
    try:
        body = json.loads(request.body)
        data = body.get('data')
        value = body.get('value')
        if user.update(data, value) is None:
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
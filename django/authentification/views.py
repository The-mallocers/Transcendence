import json
import bcrypt

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import User
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def register(req):

    users = User.objects.all()
    context = {"users": users}

    if req.method == 'GET':
        return render(req, "index.html", context)

    if req.method == 'POST':
        body_unicode = req.body.decode('utf-8')
        body = json.loads(body_unicode)
        salt = bcrypt.gensalt(prefix=b'2b')
        newUser = User(
            name = body['name'],
            nickname = body['nickname'],
            email = body['email'],
            password = bcrypt.hashpw(body['password'].encode('utf-8'), salt).decode("utf-8")
        )
        newUser.save()
        return JsonResponse({"response": 200})

@csrf_exempt
def login(req):

    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)

    user = User.objects.filter(email=body['email']).first()
    password = user.password.encode('utf-8')

    if req.method == 'POST':
        return JsonResponse({"isGoodPass": bcrypt.checkpw(body['password'].encode('utf-8'), password)})
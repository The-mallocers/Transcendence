from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from shared.models import User

def index_view(req):
    if req.method == 'GET':
        return get(req)
    if req.method == 'POST':
        return post(req)
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not allowed"
        }, status=405)

def get(req):
    users = User.objects.all()
    context = {"users": users}
    return render(req, "index.html", context)

def post(req):
    return HttpResponse("index")
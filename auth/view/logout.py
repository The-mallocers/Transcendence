import uuid

from django.http import HttpResponseRedirect, JsonResponse

from shared.models import User


def logout_view(req):
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
    return HttpResponseRedirect('/')

def post(req):
    user = User.get_user(req)
    if user:
        user.session_user = uuid.uuid4()
        user.save()

    response = JsonResponse({
        "success": True,
        "message": "Logout successefuly",
        "redirect_url": "/"
    }, status=200)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
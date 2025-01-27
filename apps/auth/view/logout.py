from django.http import JsonResponse

def post(req):
    response = JsonResponse({
        "success": True,
        "message": "Logout successefuly",
        "redirect_url": "/"
    }, status=200)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
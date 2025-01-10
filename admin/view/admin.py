from django.http import JsonResponse
from django.shortcuts import render

def admin_view(req):
    if req.method == 'GET':
        return get(req)
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not allowed"
        }, status=405)

def get(req):
    return render(req, "admin/admin.html", status=404)
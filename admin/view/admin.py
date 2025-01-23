from django.shortcuts import render

def get(req):
    return render(req, "admin/admin.html")

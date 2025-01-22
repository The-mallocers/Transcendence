from django.shortcuts import render

def get(req):
    return render(req, "error/404.html", status=404)
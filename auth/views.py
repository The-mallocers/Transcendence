from django.views.decorators.csrf import csrf_exempt

from auth.view.login import login_view
from auth.view.logout import logout_view
from auth.view.register import register_view


@csrf_exempt
def register(req):
    return register_view(req)

@csrf_exempt
def login(req):
    return login_view(req)

@csrf_exempt
def logout(req):
    return logout_view(req)

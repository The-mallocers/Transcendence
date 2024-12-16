from django.views.decorators.csrf import csrf_exempt

from authentification.view.login import login_view
from authentification.view.logout import logout_view
from authentification.view.register import register_view


@csrf_exempt
def register(req):
    return register_view(req)

@csrf_exempt
def login(req):
    return login_view(req)

@csrf_exempt
def logout(req):
    return logout_view(req)

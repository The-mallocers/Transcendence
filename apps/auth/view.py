from django.views.decorators.http import require_http_methods

from apps.auth.views.login import get as get_login
from apps.auth.views.register import get

from apps.auth.views.twofa import view_two_fa
from apps.auth.views.auth42 import auth42


@require_http_methods(["GET"])
def register_get(req):
    return get(req)


@require_http_methods(["GET"])
def login_get(req):
    return get_login(req)


@require_http_methods(["GET"])
def twofa_get(req):
    return view_two_fa(req)

# @require_http_methods(["GET"])
def exchange_42_token(req):
    print("aaaaaaaaaaaaa")
    return auth42(req)

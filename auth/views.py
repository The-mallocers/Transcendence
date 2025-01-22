from django.views.decorators.http import require_http_methods

from auth.view.login import post as post_login, get as get_login
from auth.view.logout import post as post_logout
from auth.view.register import post, get


@require_http_methods(["POST"])
def register_post(req):
    return post(req)

@require_http_methods(["GET"])
def register_get(req):
    return get(req)

@require_http_methods(["POST"])
def login_post(req):
    return post_login(req)

@require_http_methods(["GET"])
def login_get(req):
    return get_login(req)

@require_http_methods(["POST"])
def logout(req):
    return post_logout(req)

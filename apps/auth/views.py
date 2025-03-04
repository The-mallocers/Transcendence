from django.views.decorators.http import require_http_methods

from apps.auth.view.login import get as get_login
from apps.auth.view.register import get


@require_http_methods(["GET"])
def register_get(req):
    return get(req)

@require_http_methods(["GET"])
def login_get(req):
    return get_login(req)

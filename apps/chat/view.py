# Create your views here.
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def chat_get(req):
    from apps.chat.views.chat import get
    return get(req)


@require_http_methods(["GET"])
def friend_request_get(req):
    from apps.chat.views.friend_request import get
    return get(req)

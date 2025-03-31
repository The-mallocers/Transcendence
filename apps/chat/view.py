# Create your views here.
from django.views.decorators.http import require_http_methods

from apps.chat.views.chat import get


@require_http_methods(["GET"])
def chat_get(req):
    return get(req)

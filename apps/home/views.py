from django.views.decorators.http import require_http_methods

from apps.home.view.index_view import get

@require_http_methods(["GET"])
def index_get(req):
    return get(req)

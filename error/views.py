from django.views.decorators.http import require_http_methods

from error.view.error_404 import get


@require_http_methods(["GET"])
def error404_get(request, exception):
    return get(request)

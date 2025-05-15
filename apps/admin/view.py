from django.views.decorators.http import require_http_methods

from apps.admin.views.admin import get_monitoring

@require_http_methods(["GET"])
def get(req):
    return get_monitoring(req)
from django.views.decorators.http import require_http_methods

from admin.view.admin import get


@require_http_methods(["GET"])
def admin_get(request):
    return get(request)

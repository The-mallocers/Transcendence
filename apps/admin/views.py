from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def admin_get(request):
    from apps.admin.view.admin import get
    return get(request)


@require_http_methods(["GET"])
def edit_user_get(request, client_id):
    from apps.profile.view.profile import get
    return get(request, client_id)

from django.views.decorators.http import require_http_methods

from apps.profile.view.profile import get, get_settings , post, delete


@require_http_methods(["GET"])
def profile_get(req):
    return get(req)

@require_http_methods(["GET"])
def settings_get(req):
    print('huuuh')
    return get_settings(req)

@require_http_methods(["POST"])
def profile_post(req, client_id):
    return post(req, client_id)


@require_http_methods(["DELETE"])
def profile_delete(req, client_id):
    return delete(req, client_id)

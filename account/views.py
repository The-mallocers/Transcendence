from django.views.decorators.http import require_http_methods

from account.view.account import get, post, delete


@require_http_methods(["GET"])
def account_get(req):
    return get(req)


@require_http_methods(["POST"])
def account_post(req, client_id):
    return post(req, client_id)


@require_http_methods(["DELETE"])
def account_delete(req, client_id):
    return delete(req, client_id)

from django.views.decorators.http import require_http_methods

from account.view.account import get, post, delete


@require_http_methods(["GET"])
def account_get(req):
    return get(req)


@require_http_methods(["POST"])
def account_post(req):
    return post(req)


@require_http_methods(["DELETE"])
def account_delete(req):
    return delete(req)

from django.views.decorators.csrf import csrf_exempt

from account.view.account import account_view

@csrf_exempt
def account(req):
    return account_view(req)
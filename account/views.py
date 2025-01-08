from django.views.decorators.csrf import csrf_exempt

from account.view.account import account_view
from utils.decorators.activity_checker import activity_checker
from utils.decorators.jwt_required import jwt_required

@csrf_exempt
@jwt_required
@activity_checker
def account(req):
    return account_view(req)
from django.views.decorators.csrf import csrf_exempt

from account.view.account import account_view
from utils.decorators.jwt_required import jwt_required


# Create your views here.
@csrf_exempt
def account(req):
    return account_view(req)
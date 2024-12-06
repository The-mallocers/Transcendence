from django.shortcuts import render
from .models import User
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def index(req):

    users = User.objects.all()
    context = {"users": users}
    
    if (req.method == 'POST'):
        newUser = User(
            name = "mathieu",
            nickname = "ez2c",
            email = "ez2Cmail",
            password = "lalala"
        )
        newUser.save()

    return render(req, "index.html", context)


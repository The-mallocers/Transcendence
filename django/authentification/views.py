from django.shortcuts import render
from .models import User

# Create your views here.
def index(req):

    print(req.method)
    # if (req.method == 'GET'):
    users = User.objects.all()
    context = {"users":users}
    return render(req, "index.html", context)
    
    # elif (req.method == 'POST'):
    #     return 

    # if (req.)


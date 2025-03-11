from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

def get(req):
    users = Clients.objects.all()
    # Get the CSRF token
    csrf_token = get_token(req)
    
    # Render the HTML template to a string
    html_content = render_to_string("apps/auth/login.html", {"users": users, "csrf_token": csrf_token})
    
    # Return both the HTML and any additional data
    return JsonResponse({
        'html': html_content,
        'users': list(users.values())
    })
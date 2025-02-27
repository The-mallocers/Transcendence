from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

# Create your views here.

def chat(request):
    html_content = render_to_string("apps/chat/chat.html", {"csrf_token": get_token(request), 'my_range': range(10)})
    return JsonResponse({
        'html': html_content,
    })


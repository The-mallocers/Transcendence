from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string


def get(request):
    print("We are in the proper Disconnect page view (in spite of all odds)")
    message = "Opponent Left"
    # Lets add something cute here to get a random message everytime.
    html_content = render_to_string("pong/../../templates/apps/pong/disconnect.html", {
        "csrf_token": get_token(request),
        "message": message,
    })
    return JsonResponse({
        'html': html_content,
    })

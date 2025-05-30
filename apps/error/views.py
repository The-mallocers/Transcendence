from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string


# this will get the number of the error later.
def error(request, error_code=404):
    html_content = render_to_string("apps/error/404.html", {
        "csrf_token": get_token(request),
        "error_code": error_code
    })
    return JsonResponse({
        'html': html_content,
    }, status=error_code)

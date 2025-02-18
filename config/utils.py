from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

#Ill put all my useful functions that we'll import here, but as of right now
#I am still searching for the explanations of a lot of different behaviors
def handle_spa_request(request, template_name, context=None):
    """
    Universal handler for both direct page loads and AJAX requests in a SPA.
    
    Args:
        request: The HTTP request object
        template_name: Name of the template to render
        context: Dictionary of context data for the template
    """
    if context is None:
        context = {}
    
    # Ensure CSRF token is available in context
    context['csrf_token'] = get_token(request)
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        # For AJAX requests, just return the content template
        html_content = render_to_string(f"apps/{template_name}.html", context)
        return JsonResponse({'html': html_content})
    else:
        # For direct page loads, render the full page
        # Add the content template to the context
        context['content_template'] = f"apps/{template_name}.html"
        return HttpResponse(render_to_string("apps/base.html", context))
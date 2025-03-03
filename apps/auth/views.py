from django.views.decorators.http import require_http_methods

from apps.auth.view.login import post as post_login, get as get_login
from apps.auth.view.logout import post as post_logout
from apps.auth.view.register import post, get
import os, requests
from django.http import JsonResponse, HttpResponse


@require_http_methods(["POST"])
def register_post(req):
    return post(req)

@require_http_methods(["GET"])
def register_get(req):
    return get(req)

@require_http_methods(["POST"])
def login_post(req):
    return post_login(req)

@require_http_methods(["GET"])
def login_get(req):
    return get_login(req)

@require_http_methods(["POST"])
def logout(req):
    return post_logout(req)

@require_http_methods(["GET"])
def render_dashboard(request) -> str:
    secretkey = os.environ.get('GRAFANA_BEARERKEY')
    print(secretkey)
    api_url = "http://grafana:3000/api/search?type=dash-db"
    
    my_headers = {
        'Accept': 'application/json',
        "Content-Type": "application/json",
    "Authorization": f'Bearer {secretkey}'
    }
    try:
        response = requests.get(
            api_url,
            params=request.GET.dict(),  # Pass along all query parameters
            headers=my_headers
        )
        response.raise_for_status()
        data = response.json()
        print(data)
        url = data[0].get('url')
        return url
    
    except requests.exceptions.RequestException as e:
        print(str(e))
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def grafana_proxy(request):
    print("dans grafana_proxy")
    secretkey = os.environ.get('GRAFANA_BEARERKEY')
    
    # Step 1: Get the dashboard URL from the API
    api_url = "http://grafana:3000/api/search?type=dash-db"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {secretkey}'
    }
    
    try:
        # Get the dashboard URL
        api_response = requests.get(
            api_url,
            params=request.GET.dict(),
            headers=headers
        )
        api_response.raise_for_status()
        data = api_response.json()
        dashboard_url = data[0].get('url')
        
        print(api_response)
        # Step 2: Get the actual dashboard content
        dashboard_full_url = f'http://grafana:3000{dashboard_url}?refresh=5s&kiosk'
        dashboard_response = requests.get(
            dashboard_full_url,
            headers={
                'Authorization': f'Bearer {secretkey}'
            }
        )
        print(dashboard_response)
        
        # Return the dashboard content
        django_response = HttpResponse(
            content=dashboard_response.content,
            status=dashboard_response.status_code,
            content_type=dashboard_response.headers.get('Content-Type', 'text/html')
        )
        
        # Copy relevant headers, excluding those that might cause issues
        for header, value in dashboard_response.headers.items():
            if header.lower() not in ['content-encoding', 'content-length', 'x-frame-options']:
                django_response[header] = value
        
        # Allow embedding in iframe
        django_response['X-Frame-Options'] = 'SAMEORIGIN'
        
        print(django_response)
        return django_response
        
    except requests.exceptions.RequestException as e:
        print(str(e))
        return HttpResponse(f"Error: {str(e)}", status=500)
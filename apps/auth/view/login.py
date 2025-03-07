from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

import requests, os


def get(req):
    csrf_token = get_token(req)
    urlnode, urlsql = None, None
    #Commenting this because this was causing logout to crash (but for some reason not just getting to the page)
    urlnode, urlsql = render_dashboard(req)
    users = Clients.objects.all()
    print(urlnode)
    print(urlsql)
    # Render the HTML template to a string
    html_content = render_to_string("apps/auth/login.html", {
        "users": users, 
        "csrf_token": csrf_token,
        "urlnode" :urlnode,
        "urlsql" : urlsql
        })
    
    # Return both the HTML and any additional data
    return JsonResponse({
        'html': html_content,
        'users': list(users.values())
    })


# For an API endpoint that returns JSON directly:
def render_dashboard(request) -> str:
    secretkey = os.environ.get('GRAFANA_BEARERKEY')
    api_url = "http://grafana:3000/api/search?type=dash-db"
    print(api_url)
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
        print(response)
        data = response.json()
        print(data)
        urlnode = data[0].get('url')
        urlsql = data[1].get('url')
        return urlnode, urlsql
    
    except requests.exceptions.RequestException as e:
        print(str(e))
        return JsonResponse({'error': str(e)}, status=500)
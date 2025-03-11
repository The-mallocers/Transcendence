from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

import requests, os, json

id = 0

def get(req):
    csrf_token = get_token(req)
    # new_user = create_user()
    # if new_user:
    secretKey = create_api_key()
    urlnode, urlsql = None, None
    #Commenting this because this was causing logout to crash (but for some reason not just getting to the page)
    # urlnode, urlsql = render_dashboard(req, secretKey)
    users = Clients.objects.all()
    print(id)
    # print(urlnode)
    # print(urlsql)
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

def create_api_key():
    global id
    grafana_url = "http://grafana:3000"
    admin_user = "admin"
    admin_password = os.environ.get('GRAFANA_PASSWORD')
    create_key_url = f"{grafana_url}/api/serviceaccounts"
    
    # API key details
    key_data = {
        "name": "grafanaDashboard",
        "role": "Admin"  # Can be "Admin", "Editor", or "Viewer"
    }
    
    # Make the API request
    response = requests.post(
        create_key_url,
        headers={"Content-Type": "application/json"},
        auth=(admin_user, admin_password),
        data=json.dumps(key_data)
    )
    if response.status_code == 200 or response.status_code == 201:
        print(response.json())
        id = response.json().get('id')
        print(id)
        return response.json()
    else:
        print(f"Failed to create API key. Status code: {response.status_code}")
        url = "http://grafana:3000/api/serviceaccounts/7/tokens"
        dataJson = {"name":"grafanaToken"}
        res = requests.post(url,
                     headers={"Content-Type": "application/json"},
                     auth=(admin_user, admin_password),
                     data=json.dumps(dataJson))
        print("status code: " + str(res))
        print(res.json().get('key'))
        return res.json().get('key')

# For an API endpoint that returns JSON directly:
def render_dashboard(request, secretkey) -> str:
    # secretkey = os.environ.get('GRAFANA_BEARERKEY')
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
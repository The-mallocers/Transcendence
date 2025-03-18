from django.conf import settings
from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

import requests, json

grafana_id = 0

def get(req):
    csrf_token = get_token(req)
    urlnode, urlsql = None, None
    grafana_session = authenticate_grafana_user()
    secretKey = create_api_key(grafana_session)
    urlnode, urlsql = render_dashboard(req, secretKey, grafana_session)
    # #Commenting this because this was causing logout to crash (but for some reason not just getting to the page)
    users = Clients.objects.all()
    print(grafana_id)
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

def authenticate_grafana_user():
    login_url = "http://grafana:3000/login"
    session = requests.Session()
    admin = "admin"
    pwd = settings.GRFANA_ADMIN_PWD
    # Grafana typically uses a login form
    response = session.post(
        login_url,
        json={"user": admin, "password": pwd},
        headers={"Content-Type": "application/json"}
    )
    print(session)
    
    # Check if login was successful
    if response.status_code == 200:
        return session
    else:
        print(f"Failed to authenticate: {response.status_code}, {response.text}")
        return None

def create_api_key(session):
    admin_client = Clients.get_client_by_email(settings.ADMIN_EMAIL)
    admin_user = "admin"
    admin_password = settings.GRFANA_ADMIN_PWD
    url = f"http://grafana:3000/api/serviceaccounts"
    
    # API key details
    key_data = {
        "name": "grafanaDashboard",
        "role": "Admin" 
    }
    if admin_client.rights.grafana_id != 0 and admin_client.rights.grafana_token not in (None, ''):
        return admin_client.rights.grafana_token
    else :
        # Make the API request
        response = session.post(
            url,
            headers={"Content-Type": "application/json"},
            auth=(admin_user, admin_password),
            data=json.dumps(key_data)
        )
        if response.status_code == 200 or response.status_code == 201:
            grafana_id = response.json().get('id')
            admin_client.rights.grafana_id = grafana_id
            url = f"http://grafana:3000/api/serviceaccounts/{grafana_id}/tokens"
            dataJson = {"name":"grafanaToken"}
            res = session.post(url,
                        headers={"Content-Type": "application/json"},
                        auth=(admin_user, admin_password),
                        data=json.dumps(dataJson))
            admin_client.rights.grafana_token = res.json().get('key')
            admin_client.rights.save()
            return res.json().get('key')
        return admin_client.rights.grafana_token

# For an API endpoint that returns JSON directly:
def render_dashboard(request, secretkey, session) -> str:
    print(secretkey )
    api_url = "http://grafana:3000/api/search?type=dash-db"
    my_headers = {
        'Accept': 'application/json',
        "Content-Type": "application/json",
        "Authorization": f'Bearer {secretkey}'
    }
    try:
        response = requests.get(
            api_url,
            headers=my_headers
        )
        response.raise_for_status()
        data = response.json()
        print(data)
        print(data[0].get('uid'))
        print(data[1].get('uid'))
        payload = {
            "timeSelectionEnabled": True,
            "isEnabled": True,  # This is the key setting
            "annotationsEnabled": True,
            "share": "public",
            "uid" : data[0].get('uid')
        }
        uidnode = data[0].get('uid')
        uidpostgre = data[1].get('uid')
        
        #get node dahsboard id
        # url = f"http://grafana:3000/api/dashboards/uid/{uidnode}/public-dashboards/"
        # response = requests.post(
        #     url,
        #     json=payload,
        #     headers=my_headers
        # )
        # response.raise_for_status()
        # data = response.json()
        # urlnode = f"http://localhost:3000/public-dashboards/{data.get('uid')}"
        urlnode = "http://localhost:3000/d/rYdddlPWk/node-exporter-full"
        
        
        #get postgres dashboard id
        # url = f"http://grafana:3000/api/dashboards/uid/{uidpostgre}/public-dashboards/"
        # response = requests.post(
        #     url,
        #     headers=my_headers
        # )
        # response.raise_for_status()
        # data = response.json()
        # urlpostgre = f"http://localhost:3000/public-dashboards/{data.get('uid')}"
        urlpostgre = "http://localhost:3000/public-dashboards/92001fadcb3b4a74ab15e272e729d10e"
        return urlnode, urlpostgre
    
    except requests.exceptions.RequestException as e:
        print(str(e))
        return JsonResponse({'error': str(e)}, status=500)
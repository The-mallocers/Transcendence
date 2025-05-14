from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

from apps.client.models import Clients
from django.conf import settings

import requests, json

def get_monitoring(request):
    client = Clients.get_client_by_request(request)
    urlpostgres = None
    grafana_session = authenticate_grafana_user()
    secretKey = create_api_key(grafana_session)
    urlpostgres = render_dashboard(request, secretKey, grafana_session)
    print(urlpostgres)
    if client is not None:
        context = {
            "client": client,
            "urlpostgres" : urlpostgres
        }
    html_content = render_to_string("apps/admin/monitoring.html", context)
    return JsonResponse({
        'html': html_content,
    })
    
def authenticate_grafana_user():
    login_url = "http://grafana:3000/login"
    session = requests.Session()
    admin = "admin"
    pwd = settings.GRFANA_ADMIN_PWD
    response = session.post(
        login_url,
        json={"user": admin, "password": pwd},
        headers={"Content-Type": "application/json"}
    )
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
    
    key_data = {
        "name": "grafanaDashboard",
        "role": "Admin" 
    }
    if admin_client.rights.grafana_id != 0 and admin_client.rights.grafana_token not in (None, ''):
        return admin_client.rights.grafana_token
    else :
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

def render_dashboard(request, secretkey, session) -> str:
    admin_client = Clients.get_client_by_email(settings.ADMIN_EMAIL)
    api_url = "http://grafana:3000/api/search?type=dash-db"
    my_headers = {
        'Accept': 'application/json',
        "Content-Type": "application/json",
        "Authorization": f'Bearer {secretkey}'
    }
    try:
        if admin_client.rights.grafana_dashboard == None:
            response = session.get(
                api_url,
                headers=my_headers
            )
            response.raise_for_status()
            data = response.json()
            payload = {
                "timeSelectionEnabled": True,
                "isEnabled": True,
                "annotationsEnabled": True,
                "share": "public",
                "uid" : data[0].get('uid')
            }
            uidpostgres = data[0].get('uid')
            url = f"http://grafana:3000/api/dashboards/uid/{uidpostgres}/public-dashboards/"
            response = session.post(
                url,
                json=payload,
                headers=my_headers
            )
            response.raise_for_status()
            data = response.json()
            urlpostgres = f"http://localhost:3000/public-dashboards/{data.get('accessToken')}"
            admin_client.rights.grafana_dashboard = urlpostgres
            admin_client.rights.save()
            return urlpostgres
        return admin_client.rights.grafana_dashboard
    
    except requests.exceptions.RequestException as e:
        print(str(e))
        return JsonResponse({'error': str(e)}, status=500)
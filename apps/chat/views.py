from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

from apps.shared.models import Clients
from apps.chat.models import Rooms
    

# Create your views here.

def chat(request):
    #TimeStamp
    #Id of sender
    #message_content
    
    client = Clients.get_client_by_request(request)
    rooms  = Rooms.get_room_by_client_id(client.id)
    me = None
    if client:
        me = client.id
    
    html_content = render_to_string("apps/chat/chat.html", {
        "csrf_token": get_token(request), 
        'my_range': range(0),
        "client_id" : me,
        "client" : client,
        "rooms" : rooms
        }),
        
    return JsonResponse({
        'html': html_content,
    })

def friendrequest(request):
    client = Clients.get_client_by_request(request)
    username = request.GET.get('username', None)
    
    print(f"Received username: {username}")
    html_content = render_to_string("apps/profile/myinformations.html", {
        "csrf_token": get_token(request),
        "isAdmin": client.rights.is_admin,
        "client" : client,
        }),
    return JsonResponse({
        'html': html_content,
    })
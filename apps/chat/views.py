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
    rooms  = Rooms.get_room_id_by_client_id(client.id)
    
    me = None
    if client:
        me = client.id
#     conversation = [
#     {
#         "sender": me,
#         "timestamp" : 345678567,
#         "content" : "yo la team"
#     },
#     {
#         "sender": "UUIDRDyrfhtyi!",
#         "timestamp" : 345678567,
#         "content" : "hellowwww"
#     },
#     {
#         "sender": "UUIDRDyrfhtyi!",
#         "timestamp" : 345678567,
#         "content" : "go faire une game"
#     }
# ]
    conversation = [] 
    
    html_content = render_to_string("apps/chat/chat.html", {
        "csrf_token": get_token(request), 
        'my_range': range(0),
        'conversation': conversation,
        "client_id" : me,
        "rooms" : rooms
        }),
        
        

    return JsonResponse({
        'html': html_content,
    })


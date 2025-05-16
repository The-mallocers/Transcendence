from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.chat.models import Rooms
from apps.client.models import Clients


def get(req):
    client = Clients.get_client_by_request(req)
    rooms = Rooms.get_room_id_by_client_id(client.id)



    me = None
    if client:
        me = client.id
    conversation = []

    html_content = render_to_string("apps/chat/chat.html", {
        "csrf_token": get_token(req),
        'my_range': range(0),
        'conversation': conversation,
        "client_id": me,
        "rooms": rooms,
    }),

    return JsonResponse({
        'html': html_content,
    })

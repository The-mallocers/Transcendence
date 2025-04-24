from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


def get(request):
    client = Clients.get_client_by_request(request)
    friends_list = client.get_all_friends()
    # print(friends_list)
    for friend in friends_list:
        print(friend)
        print(friend['client'])
    html_content = render_to_string("apps/pong/gamemodes.html",
                                    {"csrf_token": get_token(request),
                                     "friends_list" : friends_list})
    return JsonResponse({
        'html': html_content,
    })

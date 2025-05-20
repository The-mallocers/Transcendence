from json import JSONDecodeError
import json
import re
from time import sleep
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from apps.auth.api.views import formulate_json_response
from utils.enums import RTables
from utils.redis import RedisConnectionPool
from redis.commands.json.path import Path

from apps.client.models import Clients


def create_tournament(request):
    client = Clients.get_client_by_request(request)
    if isInTournament(client):
        return formulate_json_response(True, 302, "Login Successful", "/pong/tournament/tree/")
    html_content = render_to_string("apps/pong/createTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def join_tournament(request):
    client = Clients.get_client_by_request(request)
    if isInTournament(client):
        return formulate_json_response(True, 302, "Login Successful", "/pong/tournament/tree/")
    html_content = render_to_string("apps/pong/joinTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })


def inRoom(request):
    html_content = render_to_string("apps/pong/tournamentRoom.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })


def tournamentTree(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("apps/pong/tree.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def isInTournament(client) -> bool:
        inTournament = False
        redis = RedisConnectionPool.get_sync_connection("tournament_check")
        queues = check_in_queue(client, redis)
        
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
           inTournament = True 
        return inTournament

def check_in_queue(client, redis):
    cursor = 0
    if redis.hget(name=RTables.HASH_G_QUEUE, key=str(client.id)):
        return RTables.HASH_G_QUEUE
    
    while True:
        cursor, keys = redis.scan(cursor=cursor, match=RTables.HASH_QUEUE('*'))
        for key in keys:
            ready = redis.hget(key, str(client.id))
            if ready and ready.decode('utf-8') == 'True':
                return key
        if cursor == 0:
            break
    
    return None
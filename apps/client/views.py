from json import JSONDecodeError
import json
import re
from time import sleep
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from utils.enums import RTables
from utils.redis import RedisConnectionPool
from redis.commands.json.path import Path

from apps.client.models import Clients


def create_tournament(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("apps/pong/createTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def join_tournament(request):
    client = Clients.get_client_by_request(request)
    rooms = [
        {
            "name" : "minimeow's room",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 6
        },
        {
            "name" : "huh",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 4
        },
        {
            "name" : "huh2",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 8
        },
        {
            "name" : "huh3",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 7
        }
    ]
    html_content = render_to_string("apps/pong/joinTournament.html", {"csrf_token": get_token(request), "client": client, "rooms": rooms})
    return JsonResponse({
        'html': html_content,
    })

def check_in_queue(client, redis):
    """Synchronous version of acheck_in_queue"""
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

def get_pending_tournament_invitations(request):
    client = Clients.get_client_by_request(request)
    if client is None:
        return JsonResponse({"error": "Not logged in"}, status=403)
    
    redis = RedisConnectionPool.get_connection('get_pending_tournament_invitations')
    try:
        invitations = []
        cursor = 0
        
        while True:
            cursor, keys = redis.scan(cursor=cursor, match=f"{RTables.HASH_TOURNAMENT_INVITATION}:*:{client.id}")
            
            for key in keys:
                key_decoded = key.decode('utf-8')
                invitation_data = redis.hgetall(key)
                
                if not invitation_data:
                    continue
                
                tournament_code = invitation_data.get(b'tournament_code', b'').decode('utf-8')
                inviter_id = invitation_data.get(b'inviter_id', b'').decode('utf-8')
                
                tournament_info = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code))
                if not tournament_info:
                    continue
                
                inviter = Clients.get_client_by_id(inviter_id)
                if not inviter:
                    continue
                
                invitations.append({
                    "tournament_code": tournament_code,
                    "tournament_name": tournament_info["title"],
                    "inviter_username": inviter.profile.username
                })
            
            if cursor == 0:
                break
        
        return JsonResponse(invitations, safe=False)
    finally:
        RedisConnectionPool.close_connection('get_pending_tournament_invitations')
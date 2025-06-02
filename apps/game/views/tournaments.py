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

from apps.tournaments.models import Tournaments
from apps.client.models import Clients

NO_TOURNEY = 0
HALF_TOURNEY = 1
FULL_TOURNEY = 2

def create_tournament(request):
    client = Clients.get_client_by_request(request)
    status = isInTournament(client)
    if status == FULL_TOURNEY:
        return formulate_json_response(True, 302, "Redirecting to tournament", "/pong/tournament/tree/")
    elif status == HALF_TOURNEY:
        return formulate_json_response(True, 302, "Redirecting to lobby", "/pong/tournament/")
    html_content = render_to_string("apps/pong/createTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def join_tournament(request):
    client = Clients.get_client_by_request(request)
    status = isInTournament(client)
    if status == FULL_TOURNEY:
        return formulate_json_response(True, 302, "Redirecting to tournament", "/pong/tournament/tree/")
    elif status == HALF_TOURNEY:
        return formulate_json_response(True, 302, "Redirecting to lobby", "/pong/tournament/")
    html_content = render_to_string("apps/pong/joinTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })


def inRoom(request):
    client = Clients.get_client_by_request(request)
    status = isInTournament(client)
    if status == FULL_TOURNEY:
        return formulate_json_response(True, 302, "Redirecting to tournament", "/pong/tournament/tree/")
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

def tournamentTreeQuery(request):
    tournamentCode = request.GET.get("code", "000000")

    tournament = Tournaments.get_tournament_by_code(tournamentCode)

    if tournament is None:
        html_content = render_to_string("apps/error/404.html", {"error_code": "404"})
        return JsonResponse({
            'html': html_content,
        }, status=404)
    print("SALUT:", tournamentCode, tournament.scoreboards)
    html_content = render_to_string("apps/pong/treeHistory.html", {"csrf_token": get_token(request), "roomInfos": json.dumps(tournament.scoreboards)})
    return JsonResponse({
        'html': html_content,
    })


def isInTournament(client):
        redis = RedisConnectionPool.get_sync_connection("tournament_check")
        queues = check_in_queue(client, redis)
        if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
            code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
            tournament_info = redis.json().get(RTables.JSON_TOURNAMENT(code))
            if tournament_info['status'] == 'running':
                return FULL_TOURNEY
            else:
                return HALF_TOURNEY
        return NO_TOURNEY

def check_in_queue(client, redis):
    cursor = 0

    while True:
        cursor, keys = redis.scan(cursor=cursor, match=RTables.HASH_TOURNAMENT_QUEUE('*'))
        for key in keys:
            ready = redis.hget(key, str(client.id))
            if ready:
                return key
        if cursor == 0:
            break
    
    return None
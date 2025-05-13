from json import JSONDecodeError
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
    sleep(1)
    client = Clients.get_client_by_request(request)
    redis = RedisConnectionPool.get_sync_connection("Get_Players_Tournaments")
    print(f"redis is {redis}")
    queues = check_in_queue(client, redis)
    
    tournament_players = []
    if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
        print("Salut je suis dedans")
        code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
        print(f"code is {code}")
        tournament = redis.json().get(RTables.JSON_TOURNAMENT(code))
        print(RTables.JSON_TOURNAMENT(code))
        print("tournament: ", tournament)
        tournament_players = redis.json().get(RTables.JSON_TOURNAMENT(code), Path('clients'))
        print("tournament_players", tournament_players)
    
    context = {
        'tournament_players': tournament_players
    }
    print(context)
    #END OF TFREYDIE STUFF
    
    host = client.profile.username

    roomId = request.GET.get("roomId")
    roomInfos = {
        "name" : host,
    }

    trophee = '/media/rank_icon/' + client.get_rank(client.stats.mmr) + ".png"
    players = [
        {
            "nickname" : "EZ2C",
            "avatar" : "/static/assets/imgs/profile/default.png",
            "trophee" : trophee,
            "mmr" : 200,
            "winrate" : 60
        },
    ]
    html_content = render_to_string("apps/pong/tournamentRoom.html", {"csrf_token": get_token(request), "client": client, "players": players, "roomInfos": roomInfos})
    return JsonResponse({
        'html': html_content,
    })




def tournamentTree(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("apps/pong/tree.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })


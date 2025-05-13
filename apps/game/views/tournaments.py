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
    # sleep(1)
    # client = Clients.get_client_by_request(request)
    # redis = RedisConnectionPool.get_sync_connection("Get_Players_Tournaments")
    # queues = check_in_queue(client, redis)
    
    # tournament = None
    # tournament_ids = []
    # if queues and RTables.HASH_TOURNAMENT_QUEUE('') in str(queues):
    #     code = re.search(rf'{RTables.HASH_TOURNAMENT_QUEUE("")}(\w+)$', queues.decode('utf-8')).group(1)
    #     tournament = redis.json().get(RTables.JSON_TOURNAMENT(code))

    # tournament_ids = tournament['clients']
    # title = tournament['title']
    # max_clients = range(int(tournament['max_clients']))

    # print("tournament", tournament)
    # print("title:", title)
    # print("tournament_players:", tournament_ids)
    # players_infos = [] 
    # for id in tournament_ids:
    #     client = Clients.get_client_by_id(id)
    #     infos  = { 
    #         "id" : client.id,
    #         "nickname" : client.profile.username,
    #         "avatar" : client.profile.profile_picture.url,
    #         "trophee" : '/media/rank_icon/' + client.get_rank(client.stats.mmr) + ".png",
    #         "mmr" : client.stats.mmr,
    #     }
    #     players_infos.append(infos)

    # roomInfos = {
    #     "title" : title,
    #     "max_clients" : max_clients 
    # }

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


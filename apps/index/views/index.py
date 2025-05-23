import logging
import traceback

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients
from apps.game.models import Game
from config import settings
from utils.enums import EventType, RTables
from utils.redis import RedisConnectionPool
import uuid


def get(req):
    client = Clients.get_client_by_request(req)
    winrate = ghistory = rivals = None
    games_played = client.stats.games.all().order_by('-created_at')
    ghistory = get_last_matches(client, games_played)
    friends_list = client.get_all_friends()
    friends_pending = client.get_all_pending_request()
    rivals = get_rivals(client, games_played)
    friends_online_status = get_friends_online_status(friends_list)
    rank_picture = settings.MEDIA_URL + "/rank_icon/" + client.get_rank(client.stats.mmr) + ".png"
    online_status = "Online"
    pending_tournament_invitations = get_pending_tournament_invitations(client)
    
    if client is not None:
        winrate = get_winrate(client, games_played)
    (winrate)
    context = {
        "client": client,
        "clients": Clients.objects.all(),
        "gamesHistory": ghistory,
        "winrate": winrate,
        "winrate_angle": int((winrate / 100) * 360),
        "rivals": rivals,
        "csrf_token": get_token(req),
        "show_friend_request": False,
        "friends_list": friends_list,
        "friends_pending": friends_pending,
        "rank_picture": rank_picture,
        "online_status": online_status,
        "friends_online_status": friends_online_status,
        "pending_tournament_invitations": pending_tournament_invitations,
    }
    html_content = render_to_string("apps/profile/profile.html", context)
    return JsonResponse({'html': html_content})

def get_winrate(client, games_played) -> int:
    wins = games_played.filter(winner__client=client).count()

    total_games = games_played.count()
    if total_games == 0:
        return 0  # We dont want to divide by zero
    return int((wins / games_played.count()) * 100)

def get_last_matches(client, games_played) -> list:
    i = 0
    ghistory = []
    for game in games_played:
        if (i >= 4):
            break
        game = Game.objects.get(code=game.code)
        myPoints = 0
        enemyPoints = 0
        opponent = ""
        mmr_change = 0
        if (game.winner.client == None):
            myPoints = game.loser.score
            enemyPoints = game.winner.score
            opponent = "[REDACTED]"
            mmr_change = game.loser.mmr_change
        elif (game.loser.client == None):
            myPoints = game.winner.score
            enemyPoints = game.loser.score
            opponent = "[REDACTED]"
            mmr_change = game.winner.mmr_change
        elif (client.id == game.winner.client.id):
            myPoints = game.winner.score
            enemyPoints = game.loser.score
            opponent = game.loser.client.profile.username
            mmr_change = game.winner.mmr_change
        else:
            myPoints = game.loser.score
            enemyPoints = game.winner.score
            opponent = game.winner.client.profile.username
            mmr_change = game.loser.mmr_change

        mmr_change = f"{mmr_change:+d} mmr"
        ghistory.append({
            "opponent": opponent,
            "won": myPoints > enemyPoints,
            "myPoints": myPoints,
            "enemyPoints": enemyPoints,
            "when": game.created_at.strftime("%d %B %H:%M"),
            "mmr_change": mmr_change,
        })
        i += 1
    return ghistory

def get_rivals(client, games_played) -> dict:
    opponents = []
    valid_games = []
    for game in games_played:
        if game.winner.client is not None and game.loser.client is not None:
            valid_games.append(game)

    games_played = valid_games
    # getting all opponents
    for game in games_played:
        currOpponent = None
        if game.winner.client.id == client.id:
            currOpponent = game.loser.client
        else:
            currOpponent = game.winner.client
        if currOpponent and currOpponent not in opponents:
            opponents.append(currOpponent)

    rivals = {}
    for opponent in opponents:
        rivals[opponent.id] = {
            "games_won": 0,
            "games_lost": 0,
            "username": opponent.profile.username,
            "profile_picture": opponent.profile.profile_picture.url,
        }

    for game in games_played:
        if game.winner.client.id == client.id:
            rivals[game.loser.client.id]["games_won"] += 1
        elif game.loser.client.id == client.id:
            rivals[game.winner.client.id]["games_lost"] += 1
    sorted_rivals = sorted(
        rivals.items(),
        key=lambda item: item[1]["games_won"] + item[1]["games_lost"],
        reverse=True
    )

    top_3_rivals = dict(sorted_rivals[:3])

    return top_3_rivals

def get_pending_tournament_invitations(client):
    pending_invitations = []
    try:
        redis = RedisConnectionPool.get_sync_connection("Tournament_pending")
        
        invitation_pattern = f"{RTables.HASH_TOURNAMENT_INVITATION}:*:{client.id}"
        keys = redis.keys(invitation_pattern)
        
        for key in keys:
            try:
                invitation_data = redis.hgetall(key)
                if invitation_data and b'status' in invitation_data and invitation_data[b'status'] == b'pending':
                    tournament_code = key.decode('utf-8').split(':')[1]
                    
                    tournament_info = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code))
                    
                    inviter_id = invitation_data[b'inviter_id'].decode('utf-8')
                    inviter = Clients.get_client_by_id(uuid.UUID(inviter_id))
                    
                    if tournament_info and inviter:
                        pending_invitations.append({
                            'tournament_code': tournament_code,
                            'tournament_name': tournament_info['title'],
                            'inviter_id': inviter_id,
                            'inviter_username': inviter.profile.username
                        })
            except Exception as e:
                logging.getLogger('MainThread').error(traceback.format_exc())
    except Exception as e:
        logging.getLogger('MainThread').error(traceback.format_exc())

    return pending_invitations

def get_friends_online_status(friends):
    friend_status = {}
    redis = RedisConnectionPool.get_sync_connection("Index_get")
    for friend in friends:
        id = friend['client'].id
        username = friend['username']
        online_status = redis.hget(RTables.HASH_CLIENT(id), str(EventType.NOTIFICATION.value)) is not None
        friend_status[username] = "Online" if online_status else "Offline"
    return friend_status

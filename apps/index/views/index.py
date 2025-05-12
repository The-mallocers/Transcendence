from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients
from apps.game.models import Game
from config import settings
from utils.enums import EventType, RTables
from utils.redis import RedisConnectionPool


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
    if client is not None:
        winrate = get_winrate(client, games_played)
    print(winrate)
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

        if (game.winner.client == None):
            myPoints = game.loser.score
            enemyPoints = game.winner.score
            opponent = "[REDACTED]"
        elif (game.loser.client == None):
            myPoints = game.winner.score
            enemyPoints = game.loser.score
            opponent = "[REDACTED]"
        elif (client.id == game.winner.client.id):
            myPoints = game.winner.score
            enemyPoints = game.loser.score
            opponent = game.loser.client.profile.username
        else:
            myPoints = game.loser.score
            enemyPoints = game.winner.score
            opponent = game.winner.client.profile.username

        ghistory.append({
            "opponent": opponent,
            "won": myPoints > enemyPoints,
            "myPoints": myPoints,
            "enemyPoints": enemyPoints,
            "when": game.created_at
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


def get_friends_online_status(friends):
    friend_status = {}
    redis = RedisConnectionPool.get_sync_connection("Index_get")
    for friend in friends:
        id = friend['client'].id
        username = friend['username']
        online_status = redis.hget(RTables.HASH_CLIENT(id), str(EventType.NOTIFICATION.value)) is not None
        friend_status[username] = "Online" if online_status else "Offline"
    print("friend_status:", friend_status)
    return friend_status

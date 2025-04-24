from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients

def get(req):
    print("in index")
    client = Clients.get_client_by_request(req)
    print(client.stats, "meowmeoowwmeowmeoooooooooowwwwwwww")
    games_played = client.stats.games.all().order_by('-created_at')
    winrate = ghistory = rivals = None
    friends_list = client.get_all_friends()
    friends_pending = client.get_all_pending_request()
    rivals = get_rivals(client, games_played)
    ghistory = get_last_matches(client, games_played)
    print("game history is:", ghistory)
    if client is not None:
        winrate = get_winrate(client, games_played)
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
        "friends_pending" : friends_pending
    }
    print("Feeding into the context rivals =", rivals)
    html_content = render_to_string("apps/profile/profile.html", context)
    return JsonResponse({'html': html_content})

def get_winrate(client, games_played) -> int:
    wins = games_played.filter(winner__client=client).count()

    total_games = games_played.count()
    if total_games == 0: 
        return 0 #We dont want to divide by zero
    return int((wins / games_played.count()) * 100)

def get_last_matches(client, games_played) -> list:
    i = 0
    ghistory = []
    for game in games_played:
        if (i >= 4):
            break
        myPoints = 0
        enemyPoints = 0
        opponent = ""
        if (client.id == game.winner.id):
            myPoints = game.winner.score
            enemyPoints = game.loser.score
            opponent = game.loser.client.profile.username
        else:
            myPoints = game.loser.score
            enemyPoints = game.winner.score
            opponent = game.winner.client.profile.username

        ghistory.append({
            "opponent": opponent,
            "won": client.id == game.winner.id,
            "myPoints": myPoints,
            "enemyPoints": enemyPoints,
            "when": game.created_at
        })
        i += 1
    return ghistory

def get_rivals(client, games_played) -> dict:
    opponents = []

    # getting all opponents
    for game in games_played:
        currOpponent = None
        if game.winner.client.id == client.id:
            currOpponent = game.loser.client
        else:
            currOpponent = game.winner.client
        if currOpponent not in opponents:
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

    print("rivals after adding the maps")
    print(rivals)
    return rivals

    
 
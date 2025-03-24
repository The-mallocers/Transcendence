from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.game.manager import GameManager
from apps.shared.models import Clients

def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        Games_played = GameManager.get_games_of_player(client.player.id)
        Games_played = sorted(Games_played, key=lambda g: g.created_at, reverse=True)     

        faulty_games = False
        for game in Games_played:
            if game.winner == None:
                faulty_games = True
        
        if faulty_games == True:
            print("Removing the faulty games without a winner, fix your code/database !")
            Games_played = [game for game in Games_played if game.winner is not None]
        if client is not None:
            winrate = get_winrate(client, Games_played)
            ghistory = get_last_matches(client, Games_played)
            rivals = get_rivals(client, Games_played)
        
        context = {
            "client": client,
            "clients": Clients.objects.all(),
            "gamesHistory" : ghistory,
            "winrate" : winrate,
            "winrate_angle" : int((winrate / 100) * 360),
            "rivals": rivals, #somehow passing the dictionnary made for some hard to understand code in the html
            "csrf_token": get_token(req)
        }
        html_content = render_to_string("apps/profile/profile.html", context)
        return JsonResponse({'html': html_content})
    else:
        html_content = render_to_string("apps/auth/login.html", {"csrf_token": get_token(req)})
        return JsonResponse({
            'html': html_content,
        })

def get_winrate(client, games_played) -> int:
    total_games = len(games_played)
    if total_games == 0:
        return 0
    won_games = 0
    for game in games_played:
        if client.player.id == game.winner.id:
            won_games += 1
    return int((won_games / total_games) * 100)

def get_last_matches(client, games_played) -> list:
    i = 0
    ghistory = []
    for game in games_played :
        if (i >= 4):
            break
        myPoints    = 0
        enemyPoints = 0
        opponent = ""
        if (client.player.id == game.winner.id):
            myPoints = game.winner_score
            enemyPoints =  game.loser_score
            opponent = game.loser.nickname
        else :
            myPoints = game.loser_score
            enemyPoints =  game.winner_score
            opponent = game.winner.nickname

        ghistory.append({
            "opponent"    : opponent,
            "won"         : client.player.id == game.winner.id,
            "myPoints"    : myPoints,
            "enemyPoints" : enemyPoints,
            "when" : game.created_at    
        })
        i += 1
    return ghistory

def get_rivals(client, games_played) -> list:
    opponents = []
    
    #getting all opponents
    for game in games_played:
        currOpponent = None
        if game.winner.id == client.player.id:
            currOpponent = game.loser.id
        else:
            currOpponent = game.winner.id
        if currOpponent not in opponents:
            opponents.append(currOpponent)

    rivals = {}
    for opponent in opponents:
        currentClient = Clients.get_client_by_player(opponent)
        rivals[opponent] = {
            "games_won": 0,
            "games_lost":0,
            "profile_pic" : currentClient.profile.profile_picture,
            "username": currentClient.profile.username
        }
    
    for game in games_played:
        if game.winner.id == client.player.id:
            rivals[game.loser.id]["games_won"] += 1
        elif game.loser.id == client.player.id:
            rivals[game.winner.id]["games_lost"] += 1
    
    rivals = list(rivals.values())
    rivals = sorted(rivals, key=lambda x: x['games_won'] + x['games_lost'], reverse=True)
    rivals = rivals[:3] #getting the 3 most played players
    return rivals


    
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
        
        winrate = get_winrate(client, Games_played)
        ghistory = get_last_matches(client, Games_played)
        context = {
            "client": client,
            "clients": Clients.objects.all(),
            "gamesHistory" : ghistory,
            "winrate" : winrate,
            "winrate_angle" : int((winrate / 100) * 360),
            "csrf_token": get_token(req)
        }

        #{
        #     "avatar": "matboyer.jpg",
        #     "name"  : "Mathieu Boyer",
        #     "nickname" : "EZ4C"
        # }

        html_content = render_to_string("apps/profile/profile.html", context)
        return JsonResponse({'html': html_content})
    else:
        html_content = render_to_string("apps/auth/login.html", {"csrf_token": get_token(req)})
        return JsonResponse({
            'html': html_content,
        })

def get_winrate(client, games_played) -> int:
    total_games = len(games_played)
    print(total_games)
    won_games = 0

    for game in games_played:
        if client.player.id == game.winner.id:
            won_games += 1
    print(won_games)
    return int((won_games / total_games) * 100)

def get_last_matches(client, games_played) -> list:
    i = 0
    ghistory = []
    for game in games_played :
        if (i >= 4):
            break
        myPoints    = 0
        enemyPoints = 0
        oponnent = ""
        print(client.player.id, game.winner.id )
        if (client.player.id == game.winner.id):
            myPoints = game.winner_score
            enemyPoints =  game.loser_score
            oponnent = game.loser.nickname
        else :
            myPoints = game.loser_score
            enemyPoints =  game.winner_score
            oponnent = game.winner.nickname

        ghistory.append({
            "opponent"    : oponnent,
            "won"         : client.player.id == game.winner.id,
            "myPoints"    : myPoints,
            "enemyPoints" : enemyPoints,
            "when" : game.created_at    
        })
        i += 1
    return ghistory

# def get_rivals(client, games_played) -> list:
#     opponents = []
#     for game in games_played:
#         if games_played
#     pass



    
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


# I will fix the stats later.
def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        games_played = client.stats.games.all().order_by('-created_at')

        # debug stuff that no longer should trigger
        # faulty_games = False
        # for game in Games_played:
        #     if game.winner == None:
        #         faulty_games = True
        #         print("WARNING : Somehow, You have created a game without a winner, this is bad !")

        # if faulty_games == True:
        #     print("Removing the faulty games, fix your code !")
        #     Games_played = [game for game in Games_played if game.winner is not None]

        winrate = ghistory = rivals = None
        if client is not None:
            winrate = get_winrate(client, games_played)
            # ghistory = get_last_matches(client, Games_played)
            # rivals = get_rivals(client, Games_played)
        context = {
            "client": client,
            "clients": Clients.objects.all(),
            "gamesHistory": ghistory,
            "winrate": winrate,
            "winrate_angle": 42,  # int((winrate / 100) * 360),
            "rivals": rivals,
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
    wins = games_played.filter(winner__client=client).count()

    total_games = games_played.count()
    if total_games == 0:
        return 0

    # TFREYDIE Note -> If someone can explain to me why the code below doesnt work I will love you 4 ever.
    # for game in games_played:
    #     print("game is:", game)
    #     # print("in get winrate, winner is :", game.winner)
    #     if game.winner == None :
    #         print("UUHHH")
    #     elif client.id == game.winner.client.id:
    #         won_games += 1
    # print("won games:", won_games)
    return int((wins / games_played.count()) * 100)


def get_last_matches(client, games_played) -> list:
    i = 0
    ghistory = []
    for game in games_played:
        if (i >= 4):
            break
        myPoints = 0
        enemyPoints = 0
        oponnent = ""
        print(client.player.id, game.winner.id)
        if (client.player.id == game.winner.id):
            myPoints = game.winner_score
            enemyPoints = game.loser_score
            oponnent = game.loser.nickname
        else:
            myPoints = game.loser_score
            enemyPoints = game.winner_score
            oponnent = game.winner.nickname

        ghistory.append({
            "opponent": oponnent,
            "won": client.player.id == game.winner.id,
            "myPoints": myPoints,
            "enemyPoints": enemyPoints,
            "when": game.created_at
        })
        i += 1
    return ghistory


# Eventually this will return a dictionnary with all the
# rivals and their associated winrates in series.
def get_rivals(client, games_played) -> dict:
    opponents = []

    # getting all opponents
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
            "games_lost": 0,
            "profile_pic": currentClient.profile.profile_picture
        }

    for game in games_played:
        if game.winner.id == client.player.id:
            rivals[game.loser.id]["games_won"] += 1
        elif game.loser.id == client.player.id:
            rivals[game.winner.id]["games_lost"] += 1

    print("rivals after adding the maps")
    print(rivals)

    # I want my dictionnary to be like
    # rivals = {
    #     'opponent_id' = [
    #         games_won = number
    #         games_lost = number
    #     ],
    #     'opponent_id' = [
    #         games_won = number
    #         games_lost = number
    #     ]
    # }
    return opponents

# if (client.player.id == game.winner.id):
#     myPoints = game.winner_score
#     enemyPoints =  game.loser_score
#     oponnent = game.loser.nickname
# else :
#     myPoints = game.loser_score
#     enemyPoints =  game.winner_score
#     oponnent = game.winner.nickname

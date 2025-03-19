from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string



from apps.game.manager import GameManager

from apps.shared.models import Clients


def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        Games_played = GameManager.get_games_of_player(client.player.id)
        print("aaaaaaaaaaa ", Games_played)
        context = {
            "client": client,
            "clients": Clients.objects.all(),

            "lastEncountered": [
                {
                    "avatar": "matboyer.jpg",
                    "name"  : "Mathieu Boyer",
                    "nickname" : "ez2c"
                },                
                {
                    "avatar": "matboyer.jpg",
                    "name"  : "Mathieu Boyer",
                    "nickname" : "EZ3C"
                },
                {
                    "avatar": "matboyer.jpg",
                    "name"  : "Mathieu Boyer",
                    "nickname" : "EZ4C"
                }
            ],
            "gamesHistory" : [
                {
                    "opponent"    : "tfreydie",
                    "won"         : True,
                    "myPoints"    : 5,
                    "enemyPoints" : 0,
                    "when" : "a day ago"
                },                
                {
                    "opponent"    : "tfreydie",
                    "won"         : True,
                    "myPoints"    : 5,
                    "enemyPoints" : 0,
                    "when" : "a day ago"

                },
                {
                    "opponent"    : "tfreydie",
                    "won"         : False,
                    "myPoints"    : 5,
                    "enemyPoints" : 0,
                    "when" : "a day ago"

                },
                                {
                    "opponent"    : "tfreydie",
                    "won"         : True,
                    "myPoints"    : 3,
                    "enemyPoints" : 2,
                    "when" : "a day ago"

                }
            ],
            "csrf_token": get_token(req)
        }
        html_content = render_to_string("apps/profile/profile.html", context)
        return JsonResponse({'html': html_content})
    else:
        html_content = render_to_string("apps/auth/login.html", {"csrf_token": get_token(req)})
        return JsonResponse({
            'html': html_content,
        })
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token


from apps.shared.models import Clients

def get(req):
    client = Clients.get_client_by_request(req)
    if client is not None:
        print(client)
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
            ]
        }
        html_content = render_to_string("apps/profile/profile.html", context)
        return JsonResponse({'html': html_content})
    else:
        html_content = render_to_string("apps/auth/login.html", {"csrf_token": get_token(req)})
        return JsonResponse({
            'html': html_content,
        })
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpRequest
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients
from apps.index.views.index import get_last_matches, get_rivals, get_winrate
from apps.profile.models import Profile
from config import settings
from utils.enums import EventType, RTables
from utils.redis import RedisConnectionPool
from apps.index.views.index import get_pending_tournament_invitations 


def get(req):
    # Profile specific code
    requestUsername = req.GET.get("username", "randomUser")
    target = Clients.get_client_by_username(requestUsername)
    # do something if client not found
    if target is None : 
        html_content = render_to_string("apps/error/404.html", {"csrf_token": get_token(req), "error_code": "404"})
        return JsonResponse({
            'html': html_content,
        })
    
    #test if I have a friend
    #If I have it i dont display the friend request button
    client = Clients.get_client_by_request(req)
    me = Clients.get_client_by_request(req)
    is_friend = client.is_friend_by_id(target)
    
    show_friend_request = False
    if is_friend is False or None:
        show_friend_request = True
    if requestUsername == me.profile.username:
        show_friend_request = False
    # End of specific profile content

    client = target  # The client is not us its the target we are looking at !
    winrate = ghistory = rivals = None
    games_played = client.stats.games.all().order_by('-created_at')
    ghistory = get_last_matches(client, games_played)
    friends_list = client.get_all_friends()
    friends_pending = client.get_all_pending_request()
    rivals = get_rivals(client, games_played)
    ghistory = get_last_matches(client, games_played)
    rank_picture = settings.STATIC_URL + "assets/imgs/rank_icon/" + client.get_rank(client.stats.mmr) + ".png"
    online_status = "Loading"
    redis = RedisConnectionPool.get_sync_connection("Profile_get")
    online_status = redis.hget(RTables.HASH_CLIENT(client.id), str(EventType.NOTIFICATION.value)) is not None
    if client is not None:
        winrate = get_winrate(client, games_played)
    pending_tournament_invitations = get_pending_tournament_invitations(client)
    
    context = {
        "client": client,
        "clients": Clients.objects.all(),
        "gamesHistory": ghistory,
        "winrate": winrate,
        "winrate_angle": int((winrate / 100) * 360),
        "rivals": rivals,
        "csrf_token": get_token(req),
        "friends_list": friends_list,
        "friends_pending": friends_pending,
        "rank_picture": rank_picture,
        "online_status": "Online" if online_status else "Offline",
        "show_friend_request": show_friend_request,
        "pending_tournament_invitations": pending_tournament_invitations,
        "friends_online_status": {},  # no friends
    }
    html_content = render_to_string("apps/profile/profile.html", context)
    return JsonResponse({'html': html_content})


def get_settings(req):
    client = Clients.get_client_by_request(req)
    html_content = render_to_string("apps/profile/myinformations.html", {
        "csrf_token": get_token(req),
        "isAdmin": client.rights.is_admin,
        "twoFaEnable": client.twoFa.enable,
        "client": client,
    })
    return JsonResponse({
        'html': html_content,
    })


def post(request: HttpRequest, client_id):
    client = Clients.get_client_by_id(client_id)
    if client is not None:
        profile: Profile = client.profile
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        picture = request.FILES.get('profile_picture')
        password = request.POST.get('password')

        if email is not None:
            profile.email = email
        if username is not None:
            profile.username = username
        if first_name is not None:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if picture is not None:
            profile.profile_picture = picture
        if len(password):
            client.password.password = password
        try:
            client.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            }, status=200)
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Client not found.'
        })


def delete(request, client_id):
    client = Clients.get_client_by_id(client_id)
    if client is not None:
        client.delete()
        return JsonResponse({
            'success': True,
            'message': "Account has been deleted"
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Account not found'
        }, status=404)


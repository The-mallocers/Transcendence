from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def gamemodes_get(req):
    from apps.game.views.gamemodes import get
    return get(req)


@require_http_methods(["GET"])
def matchmaking_get(req):
    from apps.game.views.matchmaking import get
    return get(req)


@require_http_methods(["GET"])
def arena_get(req):
    from apps.game.views.arena import get
    return get(req)


@require_http_methods(["GET"])
def gameover_get(req):
    from apps.game.views.gameover import get
    return get(req)

@require_http_methods(["GET"])
def duel_get(req):
    from apps.game.views.duel import get
    return get(req)

def create_tournament_get(req):
    from apps.game.views.tournaments import create_tournament
    return create_tournament(req)

@require_http_methods(["GET"])
def join_tournament_get(req):
    from apps.game.views.tournaments import join_tournament
    return join_tournament(req)

@require_http_methods(["GET"])
def inTournamentRoom(req):
    from apps.game.views.tournaments import inRoom
    return inRoom(req)


@require_http_methods(["GET"])
def disconnect_get(req):
    from apps.game.views.disconnect import get
    return get(req)

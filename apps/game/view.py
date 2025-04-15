from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def pong_get(req):
    from apps.game.views.pong import get
    return get(req)


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
def create_tournament_get(req):
    from apps.game.views.tournaments import create_tournament
    return create_tournament(req)
from django.conf import settings

def spa_context(request):

    return {
        'PRINT': settings.PRINT,
    }
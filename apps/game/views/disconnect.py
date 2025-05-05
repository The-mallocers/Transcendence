from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
import random


def get(request):
    print("We are in the proper Disconnect page view (in spite of all odds)")
    message = "Opponent Left"
    # Lets add something cute here to get a random message everytime.
    disconnect_messages = [
    "They were probably scared of you.",
    "A win is a win!",
    "Guess they rage quit.",
    "Disconnected... or disappeared into the shadow realm.",
    "They saw your skills and noped out.",
    "Victory by technicality still counts!",
    "Outplayed... by the Wi-Fi router.",
    "Was it lag... or fear?",
    "RIP opponent — gone but not forgotten.",
    "Another one bites the dust (or the disconnect button).",
    "Their device couldn't handle your greatness.",
    "You win! Network issues: your most reliable teammate.",
    "Maybe they just went to get milk.",
    "Bravely ran away, Sir Opponent.",
]

    index = random.randint(0, len(disconnect_messages) - 1) 
    html_content = render_to_string("pong/../../templates/apps/pong/disconnect.html", {
        "csrf_token": get_token(request),
        "message": message,
        "disconnect_message": disconnect_messages[index], 
    })
    return JsonResponse({
        'html': html_content,
    })

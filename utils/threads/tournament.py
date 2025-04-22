from utils.threads.threads import Threads


# This thread wil :
# Manage the lobby and make sure everybody is in when the tournament is starting
# Do the match matchmaking for the tournament, take players as they go and match them against one another.
# After the tournament is over, clean up redis and destroy itself.
# {
#     "event": "tournament",
#     "data": {
#         "action": "create_tournament",
#         "args": {
#             "name": "Mon tournoi",
#             "max_players": 8,
#             "public": true,
#             "bots": true,
#             "points_to_win": 11,
#             "timer": 120
#         }
#     }
# }

class TournamentThread(Threads):
    def __init__(self, name):
        super().__init__(name)

    async def main(self):
        pass

    def cleanup(self):
        pass

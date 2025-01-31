Match aleatoire:

-Le player lance son matchmaking
-Ca ajoute le player dans la queue dans redis
-Le thread matchmaking trouve 2 player qui peut s'affronter
-Ca creer une game et ca ajoute les 2 player dedant
-La game s'active une fois que les 2 player sont actif dans la room (websocket)
-Ca lance la communication entre les socket pour les 2 player
-...
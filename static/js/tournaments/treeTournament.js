import { WebSocketManager } from "../websockets/websockets.js";
import { navigateTo } from "../spa/spa.js";

//In veut faire une requete a la websocket de l'etat actuel du tournoi.
//L'etat idealement, nous rend toute les infos qu'on va render sur la page.
//Comme ca, si jamais une update, on pourra juste tout reload la nouvelle tournament comme on le fait dans le lobby.

const tournamentSocket = WebSocketManager.tournamentSocket;


tournamentSocket.onmessage = ((msg)=>{
    console.log("TOURNAMENT ROOM RECEIVES THIS MESSAGE");
    console.log(msg);
    const message = JSON.parse(msg.data);
    
    if (message.event == "ERROR"){
        console.log("Error message: ", message.data.error)
        navigateTo("/pong/gamemodes/");
        // errDiv.innerHTML = message.data.error
        return
    }
    console.log("BONJOUR:", message.data);
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_INFO") {
        console.log("tournament info is :", message.data.action);
        tournament_data = message.data.content;
        populateTree(tournament_data.max_clients);
    }
})

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}

function populateTree() {
    //matboyer a l'aide
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));

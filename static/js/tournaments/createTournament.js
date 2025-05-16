import { WebSocketManager } from "../websockets/websockets.js"

const tournamentSocket = WebSocketManager.tournamentSocket;
const btn = document.querySelector("#create-btn");

function getTournamentSettings(){
    let score = document.querySelector(".score");
    let points = parseInt(score.innerHTML);
    const tournamentName = document.querySelector("#roomName").value;
    const isPrivate = document.querySelector("#isPrivate").checked;
    const maxClients = document.querySelector('#player-options input[name="tournamentPlayers"]:checked')?.value;

    const creationMessage = {
        "event": "tournament",
        "data": {
            "action": "create_tournament",
            "args": {
                "title": tournamentName,
                "max_clients": parseInt(maxClients),
                "is_public": !isPrivate,
                "has_bots": false,
                "points_to_win": points,
                "timer": 420
            }
        }
    };
    tournamentSocket.send(JSON.stringify(creationMessage));
}

btn?.addEventListener('click', ()=>{
    getTournamentSettings();
})
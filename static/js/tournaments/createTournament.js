import { WebSocketManager } from "../websockets/websockets.js"

const tournamentSocket = WebSocketManager.tournamentSocket
const btn = document.querySelector("#create-btn")

tournamentSocket.onmessage = ((msg)=>{
    console.log(msg);
})

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
    console.log("creationMessage", creationMessage);
    console.log(points, tournamentName, isPrivate);
    tournamentSocket.send(creationMessage);
}

btn?.addEventListener('click', ()=>{
    getTournamentSettings();
})
import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"

const tournamentSocket = WebSocketManager.tournamentSocket;
const btn = document.querySelector("#create-btn");
const errDiv = document.querySelector('#errDiv');

tournamentSocket.onmessage = ((msg)=>{
    console.log(msg);
    const message = JSON.parse(msg.data);

    if (message.event == "ERROR"){
        //Update the front to say theres been an error
        console.log("lalalalala: ", message.data.error)
        errDiv.innerHTML = message.data.error
        return
    }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_CREATED") {
        console.log(`/pong/tournament/${message.data.content.code}`);
        navigateTo(`/pong/tournament/?code=${message.data.content.code}`);        
    }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_LIST") {
        console.log("Infos of list of tournaments", message.data);
        //Update the front to show a button of stuff here.
    }
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
    tournamentSocket.send(JSON.stringify(creationMessage));
}

btn?.addEventListener('click', ()=>{
    getTournamentSettings();
})
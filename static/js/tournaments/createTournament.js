import { WebSocketManager } from "../websockets/websockets.js"

const tournamentSocket = WebSocketManager.tournamentSocket;
const btn = document.querySelector("#create-btn");


let minus = document.querySelector(".minus");
let plus = document.querySelector(".plus");


function decrease(){
    let score = document.querySelector(".score");
    let val = parseInt(score.innerHTML);
    if (val > 1)
        score.innerHTML = --val
}

function increase(){
    let score = document.querySelector(".score");
    let val = parseInt(score.innerHTML);
    if (val < 21) {
        score.innerHTML = ++val;
    }
}

minus?.addEventListener("click", decrease);
plus?.addEventListener("click", increase);

function getTournamentSettings(){
    let score = document.querySelector(".score");
    let points = parseInt(score.innerHTML);
    const tournamentName = document.querySelector("#roomName");
    // const isPrivate = document.querySelector("#isPrivate").checked;
    const maxClients = document.querySelector('#player-options input[name="tournamentPlayers"]:checked')?.value;

    const creationMessage = {
        "event": "tournament",
        "data": {
            "action": "create_tournament",
            "args": {
                "title": tournamentName.value.length > 0 ? tournamentName.value : tournamentName.placeholder,
                "max_clients": parseInt(maxClients),
                "is_public": true,
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
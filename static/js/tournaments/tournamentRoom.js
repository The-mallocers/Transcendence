import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
// const leave_btn = document.querySelector("#leave-btn");

const leave_tournament = {
    "event": "tournament",
    "data": {
        "action": "leave_tournament"
    }
}

function leaveTournament() {
    WebSocketManager.tournamentSocket.send(JSON.stringify(leave_tournament))
    // WebSocketManager.closeTournamentSocket();
    navigateTo("/pong/gamemodes/");
}

delete_btn?.addEventListener('click', ()=>{
    leaveTournament();
});

// leave_btn.addEventListener('click', ()=>{
//     leaveTournament();
// });

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));



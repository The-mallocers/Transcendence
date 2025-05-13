import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
const leave_btn = document.querySelector("#leave-btn");

const get_players_message = {
    "event": "tournament",
    "data": {
        "action": "list_players"
    }    
}
tournamentSocket.send(JSON.stringify(get_players_message));

tournamentSocket.onmessage = ((msg)=>{
    console.log(msg);
    const message = JSON.parse(msg.data);

    if (message.event == "ERROR"){
        //Update the front to say theres been an error
        console.log("lalalalala: ", message.data.error)
        errDiv.innerHTML = message.data.error
        return
    }
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_PLAYERS_LIST") {
        console.log(message.data);
    }
})

function leaveTournament() {
    WebSocketManager.closeTournamentSocket();
    navigateTo("/pong/gamemodes/");
}

delete_btn?.addEventListener('click', ()=>{
    leaveTournament();
});

leave_btn?.addEventListener('click', ()=>{
    leaveTournament();
});
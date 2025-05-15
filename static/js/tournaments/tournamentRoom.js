import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
const leave_btn = document.querySelector("#leave-btn");
const clientsInTournament = document.querySelector("#clientsInTournament");


let tournament_data = null;


tournamentSocket.onmessage = ((msg)=>{
    console.log("TOURNAMENT ROOM RECEIVES THIS MESSAGE");
    console.log(msg);
    const message = JSON.parse(msg.data);
    
    //This triggers at unwanted times, commenting it for now
    // if (message.event == "ERROR"){
    //     console.log("Error message: ", message.data.error)
    //     navigateTo("/pong/gamemodes/");
    //     // errDiv.innerHTML = message.data.error
    //     return
    // }
    console.log("BONJOUR:", message.data);
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_INFO") {
        tournament_data = message.data.content;
        populateTournament(tournament_data.max_clients);
    }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_PLAYER_JOIN") {
        tournamentSocket.send(JSON.stringify(get_tournament_info));
    }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_GAME_READY") {
        navigateTo("/pong/matchmaking/");
    }
})
/*
                    send_group(RTables.GROUP_TOURNAMENT(self.tournament.code),
                               EventType.TOURNAMENT,
                               ResponseAction.TOURNAMENT_PLAYER_JOIN,
                               {'id': str(client.id)})
                               */
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


function populateTournament(max_clients){
    let clientsDiv = []
    clientsInTournament.innerHTML = ``
    for (let i = 0 ; i < max_clients ; i++){
        clientsDiv.push(`
            <div class="col p-2">
            <div class="content border p-3 d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center justify-content-center gap-3">
            <div class="nickname ml-3"> waiting</div>
            <div>(add bpoyer's animation with the li dots)</div>
            </div>
            </div>
            </div>
            </div>
            `)
        }
        
        tournament_data?.players_infos?.forEach((player , i)=> {
            clientsDiv[i] = `
            <div class="col p-2">
            <div class="content border p-3 d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center justify-content-center gap-3">
                            <div class="avatarContainer">
                                    <img src="${player.avatar}" alt="">
                                    </div>
                                <div class="nickname ml-3">${ player.nickname }</div>
                            </div>

                            <div class="d-flex justify-content-center align-items-center gap-1 flex-column">
                            <img class="tropheeImg" src="${player.trophee}" alt="">
                            <div>mmr: ${ player.mmr }</div>
                            </div>

                        </div>
                        </div>
                        `
                        
                        console.log("mini meow: ", clientsDiv[i])
            });
    clientsDiv.forEach(htmlString => {
        const temp = document.createElement("div");
        temp.innerHTML = htmlString; 

        while (temp.firstChild) {
            console.log(temp.firstChild)
            clientsInTournament.appendChild(temp.firstChild);
        }
    });
}

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }    
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));



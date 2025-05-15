import { WebSocketManager } from "../websockets/websockets.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;

function joinTournament(code) {
    const message = {
        "event": "tournament",
        "data": {
            "action": "join_tournament",
            "args": {
                "code": code
            }
        }
    }
    tournamentSocket.send(JSON.stringify(message));
}

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    const joinBtn = e.target.closest('.joinTournamentBtn');
    if (joinBtn) {
        const parentRoom = joinBtn.closest('.room');
        const code = parentRoom.dataset.code ;
        console.log(code)
        joinTournament(code);
    }
});

const get_tournaments_info = {
    "event": "tournament",
    "data": {
        "action": "list_tournament"
    }    
}

let meowInterval = setInterval(() => {
    sendWhenReady(tournamentSocket, JSON.stringify(get_tournaments_info));
}, 3000);

sendWhenReady(tournamentSocket, JSON.stringify(get_tournaments_info));


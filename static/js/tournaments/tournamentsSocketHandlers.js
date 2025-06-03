import { navigateTo } from "../spa/spa.js";
import { populateTournament } from "./populateHelpers.js";
import { populateJoinTournament } from "./populateHelpers.js";
import { populateTree } from "./populateHelpers.js";
import { isGameOver } from "../apps/game/VarGame.js";
import { tournamentData } from "../apps/game/VarGame.js";
import { remove_toast, toast_message, toast_tournament } from "../apps/profile/toast.js";

// import { toast_message } from "../profile/toast.js";
// import { remove_toast } from "../profile/toast.js";
const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }    
}

export function setUpTournamentSocket (tournamentSocket) {
    tournamentSocket.onmessage = (message) => {
        const jsonData = JSON.parse(message.data);
        if (jsonData.event != "TOURNAMENT" && jsonData.event != "ERROR") return;
        const action = jsonData.data.action;
        console.log(action);
        switch (action) {

            case "HOST_LEAVE":
            case "NOT_IN_TOURNAMENT":
            case "TOURNAMENT_NOT_CREATE":
            case "TOURNAMENT_NOT_EXIST":
            case "EXCEPTION":
            case "ERROR":
            case "KEY_ERROR":
            case "SERVICE_ERROR":
                const path = window.location.pathname;
                if (path == "/pong/tournament/tree/" || path == "/pong/tournament/") {
                    remove_toast();
                    toast_message(jsonData.data.error || jsonData.data.content )
                    navigateTo("/pong/gamemodes/");
                }
                const errDiv = document.getElementById('errDiv');
                console.log(jsonData.data.error);
                if (errDiv) {
                    errDiv.innerText = "There was an error";
                }
                break;
            case "TOURNAMENT_PLAYER_LEFT" :
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                remove_toast();
                break;
            case "TOURNAMENT_GAME_FINISH":
                // if (isPlayerIngame(jsonData.data.content) == false) return;
                //I think the game might already be over by that point.
                // isGameOver.gameIsOver = true;
                // WebSocketManager.closeGameSocket();
                // navigateTo(`/pong/tournament/tree/?tree=${jsonData.data.content.tournament_code}`);
                // navigateTo(`/pong/tournament/tree/?tree=${jsonData.data.content.tournament_code}`);
                break;
                
            case "TOURNAMENT_JOIN":
                navigateTo(`/pong/tournament/?code=${jsonData.data.content}`);
                break;
                
            case "TOURNAMENT_LIST":
                populateJoinTournament(jsonData.data.content);
                break;
                
            case "TOURNAMENT_INFO":
                const tournament_data = jsonData.data.content;
                if (tournament_data.game_ready) tournamentData.gameIsReady = true;
                if (window.location.pathname == "/pong/tournament/tree/") {
                    populateTree(tournament_data);
                } else {
                    populateTournament(tournament_data);
                }
                break;
                
            case "TOURNAMENT_PLAYER_JOIN":
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
            case "TOURNAMENT_STARTING":
                navigateTo("/pong/tournament/tree/");
                break;
            case "TOURNAMENT_GAME_READY":
                remove_toast();
                let toast = toast_message("your tournament game is ready")
                
                let btn = document.createElement("div")
                btn.classList.add('btn', 'intra-btn')
                btn.innerText = 'ready'
                btn?.addEventListener('click', function(){
                    navigateTo('/pong/matchmaking/');
                    remove_toast()
                })
                // btn.dataset.route = '/pong/matchmaking/'
                toast.appendChild(btn)

                tournamentData.gameIsReady = true;
                // navigateTo("/pong/matchmaking/");
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
                
            case "TOURNAMENT_UPDATE":
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
            case "TOURNAMENTS_NOTIFICATION":
                // tournamentSocket.send(JSON.stringify(get_tournament_info));
                populateJoinTournament(jsonData.data.content);

                // tournamentSocket.send(JSON.stringify(get_tournaments_info));

                break;
            case "TOURNAMENT_CREATED":
                navigateTo(`/pong/tournament/?code=${jsonData.data.content.code}`);
                break;
                
            case "TOURNAMENT_INVITATION_SENT":
                remove_toast();
                toast_message("Invitation sent", "success");
                break;
                
            case "TOURNAMENT_PLAYER_LEFT" :
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
            case "BLOCKED_USER":
                remove_toast();
                toast_message("Cant send invitation to user block")
                break;
            case "TOURNAMENT_FULL":
                remove_toast();
                toast_message("Tournament is Full !");
                break;
            default:
                break;
        }
    }
}

function isPlayerIngame(data) {
    const gameLeft = window.GameState.left.id;
    const gameRight = window.GameState.right.id;
    if (gameLeft == data.winner || gameLeft == data.loser) {return true;}
    if (gameRight == data.winner || gameRight == data.loser) {return true;}
    return false;
}


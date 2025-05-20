import { navigateTo } from "../spa/spa.js";
import { populateTournament } from "./populateHelpers.js";
import { populateJoinTournament } from "./populateHelpers.js";
import { populateTree } from "./populateHelpers.js";
import { isGameOver } from "../apps/game/VarGame.js";
import { tournamentData } from "../apps/game/VarGame.js";
import { remove_toast, toast_message } from "../apps/profile/toast.js";

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
        switch (action) {

            case "HOST_LEAVE":
            case "NOT_IN_TOURNAMENT":
            case "ERROR":
                // console.log("Error message: ", jsonData.data.error)
                remove_toast()
                toast_message(jsonData.data.error || jsonData.data.content )
                navigateTo("/pong/gamemodes/");
                // errDiv.innerHTML = jsonData.data.error
                break;
            case "TOURNAMENT_PLAYER_LEFT" :
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
            case "TOURNAMENT_GAME_FINISH":
                if (isPlayerIngame(jsonData.data.content) == false) return;
                //I think the game might already be over by that point.
                // isGameOver.gameIsOver = true;
                // WebSocketManager.closeGameSocket();
                // navigateTo(`/pong/tournament/tree/?tree=${jsonData.data.content.tournament_code}`);
                // navigateTo(`/pong/tournament/tree/?tree=${jsonData.data.content.tournament_code}`);
                break;
                
            case "TOURNAMENT_JOIN":
                console.log("data of tournament join", jsonData.data);
                navigateTo(`/pong/tournament/?code=${jsonData.data.content}`);
                break;
                
            case "TOURNAMENT_LIST":
                populateJoinTournament(jsonData.data.content);
                break;
                
            case "TOURNAMENT_INFO":
                const tournament_data = jsonData.data.content;
                if (window.location.pathname == "/pong/tournament/tree/") {
                    populateTree(tournament_data);
                } else {
                    populateTournament(tournament_data);
                }
                break;
                
            case "TOURNAMENT_PLAYER_JOIN":
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
                
            case "TOURNAMENT_GAME_READY":
                remove_toast();
                let toast = toast_message("your tournament game is ready")
                
                let btn = document.createElement("div")
                btn.classList.add('btn', 'intra-btn')
                btn.innerText = 'ready'
                btn.dataset.route = '/pong/matchmaking/'
                toast.appendChild(btn)

                tournamentData.gameIsReady = true;
                // console.log("ALLO JE VAIS REJOUER OUUAIS");
                // navigateTo("/pong/matchmaking/");
                console.log(document.location.pathname)
                const parrent = document.querySelector(document.location.pathname.includes('tree') ?  '#tree': "#btnsRoom")
                console.log("data of tournament join", parrent);
                if (parrent) {
                    let btn = document.createElement('div')
                    btn.classList.add('btn', 'btn-primary');
                    btn.innerText = 'Ready';
                    btn.addEventListener('click', ()=>{navigateTo(`/pong/matchmaking/`);})
                    parrent.appendChild(btn)
                }
                break;
                
            case "TOURNAMENT_UPDATE":
                console.log("Im told theres been an update, so now Im asking for it !");
                tournamentSocket.send(JSON.stringify(get_tournament_info));
                break;
                
            case "TOURNAMENT_CREATED":
                console.log("CREATING TOURNAMENT !");
                navigateTo(`/pong/tournament/?code=${jsonData.data.content.code}`);
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


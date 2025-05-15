import { navigateTo } from "../spa/spa.js";
import { populateTournament } from "./populateHelpers.js";
import { populateJoinTournament } from "./populateHelpers.js";
import { populateTree } from "./populateHelpers.js";

export function setUpTournamentSocket (tournamentSocket) {

    tournamentSocket.onmessage = (message) => {
        const jsonData = JSON.parse(message.data);
        console.log("Tournament socket message", jsonData.data);
        if (message.event != "TOURNAMENT") return ;
        const action = jsonData.data.action;

        //This triggers at unwanted times, commenting it for now
        // if (message.event == "ERROR"){
        //     console.log("Error message: ", message.data.error)
        //     navigateTo("/pong/gamemodes/");
        //     // errDiv.innerHTML = message.data.error
        //     return
        // }
        if (action == "TOURNAMENT_GAME_FINISH") {
            //check this is our game thats over
            if (isPlayerIngame(jsonData.data.content) == false) { return ;}
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
            navigateTo(`/pong/tournament/tree/?tree=${jsonData.data.content.tournament_code}`);
        }
        else if (action == "TOURNAMENT_JOIN") {
            console.log("data of tournament join", jsonData.data);
            navigateTo(`/pong/tournament/?code=${jsonData.data.content}`);
        }
        else if (action == "TOURNAMENT_LIST") {
            populateJoinTournament(jsonData.data.content);
        }
        else if (action == "TOURNAMENT_INFO") {
            tournament_data = jsonData.data.content;
            if (window.location.pathname == "/pong/tournament/tree/") {
                populateTree(tournament_data);
            } else {
                populateTournament(tournament_data);
            }
        }
        else if (action == "TOURNAMENT_PLAYER_JOIN") {
            tournamentSocket.send(JSON.stringify(get_tournament_info));
        }
        else if (action == "TOURNAMENT_GAME_READY") {
            console.log("ALLO JE VAIS REJOUER OUUAIS");
            navigateTo("/pong/matchmaking/");
        }
        else if (action == "TOURNAMENT_UPDATE") {
            console.log("Im told theres been an update, so now Im asking for it !");
            tournamentSocket.send(JSON.stringify(get_tournament_info));
        }
    }
}

function isPlayerIngame(data) {
    console.log("data in function is ", data);
    console.log("window.GameState", window.GameState);
    const gameLeft = window.GameState.left.id;
    const gameRight = window.GameState.right.id;
    console.log("game left and game right", gameLeft, " ", gameRight);
    console.log("data winner and data loser", data.winner, " ", data.loser);
    if (gameLeft == data.winner || gameLeft == data.loser) {return true;}
    if (gameRight == data.winner || gameRight == data.loser) {return true;}
    return false;
}


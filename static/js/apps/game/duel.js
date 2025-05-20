import { navigateTo } from "../../spa/spa.js";
import { WebSocketManager } from "../../websockets/websockets.js";
import { toast_message } from "../profile/toast.js"; 
import { remove_toast } from "../profile/toast.js";
import { getClientId } from "../../utils/utils.js";

let clientId;

clientId = await getClientId();
const gameSocket = await WebSocketManager.initGameSocket(clientId);
const notifSocket = WebSocketManager.notifSocket;

const cancelDuel = document.querySelector(".cancel-duel");
if (cancelDuel) {
    cancelDuel.addEventListener('click', function (event) {
        navigateTo('/pong/gamemodes/')
    })
}

const opponentDiv = document.querySelector(".opponent_player");
if (opponentDiv) {
    const urlParams = new URLSearchParams(window.location.search);
    const opponentName = urlParams.get("opponent");
    opponentDiv.innerHTML = opponentName;
}

let height = 500;
const width = 1000;

const paddleHeight = 100;

let paddleDefaultPos = 250 - (paddleHeight / 2)

window.GameState = {
    ballY: height / 2,
    ballX: width / 2,

    left: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: "",
        id: ""
    },
    right: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: "",
        id: ""
    }
}

window.GameInfos = {
    left: {}
}

const startGameMessage = {
    "event": "game",
    "data": {
        "action": "start_game"
    }
}

// const message = {
//     "event": "matchmaking",
//     "data": {
//         "action": "join_queue"
//     }
// }
// gameSocket.onopen = () => {

//     socket.send(JSON.stringify(message));
// }


notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);

    if (message.data.action == "DUEL_REFUSED") {
        navigateTo("/pong/gamemodes/");
        remove_toast();
        toast_message(`${message.data.content.username} refuses the duel`);
    } else if (message.data.action == "DUEL_JOIN") {
        const pendingDiv = document.querySelector(".state-of-player");
        if (pendingDiv) {
            pendingDiv.innerHTML = "join";
            pendingDiv.style.backgroundColor = "#00babc";
            pendingDiv.style.color = "white"
        }
    } else if (message.data.action == "DUEL_CREATED") {
        navigateTo(`/pong/duel/?opponent=${message.data.content.opponent}`);
    }
    else if(message.data.action == "BLOCKED_USER"){ 
        remove_toast();
        toast_message("You have blocked this user");
        navigateTo('');
    }
}

gameSocket.onmessage = (e) => {
    const jsonData = JSON.parse(e.data);

    console.log(jsonData.data.action);
    //We should only get the response that a match was found

    //On message on regarde si c'est que la game a commencer
    //on renvois le json approprie
    if (jsonData.data.action == "PLAYER_INFOS") {
        console.log("PLAYER INFOS IS:")
        console.log(jsonData.data.content)
        window.GameState = {
            ballY: height / 2,
            ballX: width / 2,

            left: {
                x: jsonData.data.content.left.paddle.x,
                y: jsonData.data.content.left.paddle.y,
                username: jsonData.data.content.left.username,
                id: ""
            },
            right: {
                x: jsonData.data.content.right.paddle.x,
                y: jsonData.data.content.right.paddle.y,
                username: jsonData.data.content.right.username,
                id: ""
            }
        }
    }
    if (jsonData.data.action == "STARTING") {
        navigateTo("/pong/arena/");
        gameSocket.send(JSON.stringify(startGameMessage))
    }
};
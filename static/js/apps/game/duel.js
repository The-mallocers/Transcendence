import { navigateTo } from "../../spa/spa.js";
import { WebSocketManager } from "../../websockets/websockets.js";
// import { notifSocket } from "../profile/profile.js";

let client_id;
let clientId;

clientId = await getClientId();
const gameSocket = await WebSocketManager.initGameSocket(clientId);
const cancel_duel = document.querySelector('.chatRooms');
if(cancel_duel)
{
    
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

async function getClientId() {
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();

        if (data.client_id) {
            client_id = data.client_id;
            return client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}
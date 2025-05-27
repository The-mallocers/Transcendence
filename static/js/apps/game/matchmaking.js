import {navigateTo} from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"

//Fetch pour dire au serveur qu'on veut join la queue
const element = document.querySelector("#clientID");
const clientId = element.dataset.clientId

const gameStatusDiv = document.querySelector("#gameStatus")

let height = 500;
const width = 1000;

const paddleHeight = 100;

let paddleDefaultPos = 250 - (paddleHeight / 2)



WebSocketManager.closeGameSocket();
WebSocketManager.initGameSocket(clientId);
const socket = WebSocketManager.gameSocket;


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

const leftGameMessage = {
    "event": "matchmaking",
    "data": {
        "action": "leave_queue"
    }
}

window.leftQueue = function () {
    socket.send(JSON.stringify((leftGameMessage)));
    // socket.close();
    navigateTo('/pong/gamemodes/');
}

const startGameMessage = {
    "event": "game",
    "data": {
        "action": "start_game"
    }
}


const message = {
    "event": "matchmaking",
    "data": {
        "action": "join_queue"
    }
}
socket.onopen = () => {
    socket.send(JSON.stringify(message));
}
socket.onclose = (event) => {
    if (event.code === 4001) {
        navigateTo("/pong/gamemodes/");
    };
}

socket.onmessage = (e) => {
    const jsonData = JSON.parse(e.data)

    if ((typeof jsonData?.data?.content) == "string")
        gameStatusDiv.innerHTML = jsonData.data.content
    //We should only get the response that a match was found

    //On message on regarde si c'est que la game a commencer
    //on renvois le json approprie
    if (jsonData.data.action == "PLAYER_INFOS") {
        window.GameState = {
            ballY: height / 2,
            ballX: width / 2,

            left: {
                x: jsonData.data.content.left.paddle.x,
                y: jsonData.data.content.left.paddle.y,
                username: jsonData.data.content.left.username,
                id: jsonData.data.content.left.client_id,
                picture: jsonData.data.content.left.player_profile,

            },
            right: {
                x: jsonData.data.content.right.paddle.x,
                y: jsonData.data.content.right.paddle.y,
                username: jsonData.data.content.right.username,
                id: jsonData.data.content.right.client_id,
                picture: jsonData.data.content.right.player_profile,
            }
        }
    }
    if (jsonData.data.action == "STARTING") {
        navigateTo("/pong/arena/")
        socket.send(JSON.stringify(startGameMessage))
    }
    ////// navigate to arena and then startGame would be better
    // if ()
}
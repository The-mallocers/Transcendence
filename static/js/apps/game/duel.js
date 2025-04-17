import { navigateTo } from "../../spa/spa.js";
import { gameSocket } from "./gamemode.js";
import { WebSocketManager } from "../../websockets/websockets.js";

let client_id;
let clientId
let gameSocketGuest = null;
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

//if it's the guest player
const searchParams = new URLSearchParams(window.location.search);
console.log(searchParams);
if(searchParams.has("guest"))
{
    clientId = await getClientId();
    gameSocketGuest = await WebSocketManager.initGameSocket(clientId);
}

if(gameSocket)
{
    setupSocketMessageHandler(gameSocket)
}
else if(gameSocketGuest)
{
    setupSocketMessageHandler(gameSocketGuest)
}

function setupSocketMessageHandler(socket) {
    socket.onmessage = (e) => {
        const jsonData = JSON.parse(e.data);
        const { action, content } = jsonData.data;
        console.log(action);
        
        switch (action) {
            case "PLAYER_INFOS":
                console.log("PLAYER INFOS IS:");
                console.log(content);
                updateGameState(content);
                break;
                
            case "STARTING":
                navigateTo("/pong/arena/");
                socket.send(JSON.stringify(startGameMessage));
                break;
        }
    };
}

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
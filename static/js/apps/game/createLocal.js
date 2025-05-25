import {WebSocketManager} from "../../websockets/websockets.js"
import {navigateTo} from "../../spa/spa.js";
import { localState } from "./VarGame.js";

const btn = document.querySelector("#play-btn");
const element = document.querySelector("#clientID");
const clientId = element.dataset.clientId;

let height = 500;
const width = 1000;
const paddleHeight = 100;
let paddleDefaultPos = 250 - (paddleHeight / 2)


WebSocketManager.initGameSocket(clientId);
const gameSocket = WebSocketManager.gameSocket


let minus = document.querySelector(".minus");
let plus = document.querySelector(".plus");


function decrease() {
    let score = document.querySelector(".score");
    let val = parseInt(score.innerHTML);
    if (val > 1)
        score.innerHTML = --val
}

function increase() {
    let score = document.querySelector(".score");
    let val = parseInt(score.innerHTML);
    if (val < 21) {
        score.innerHTML = ++val;
    }
}

minus?.addEventListener("click", decrease);
plus?.addEventListener("click", increase);

const player_left_name = document.querySelector("#playerLeft");
const player_right_name = document.querySelector("#playerRight");

window.GameState = {
    ballY: height / 2,
    ballX: width / 2,

    left: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: player_left_name,
        id: ""
    },
    right: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: player_right_name,
        id: ""
    }
}

function getLocalSettings() {
    let score = document.querySelector(".score");
    let points = parseInt(score.innerHTML);

    const creationMessage = {
        "event": "game",
        "data": {
            "action": "local_game",
            "args": {
                "points_to_win": points,
            }
        }
    };
    gameSocket.send(JSON.stringify(creationMessage));
}

gameSocket.onmessage = (e) => {
    const message = JSON.parse(e.data);
    console.log(e.data.action);
    if (message.data.action == "GAME_CREATED") {
        console.log("IN", e.data.action);
        localState.gameIsLocal = true;
        navigateTo('/pong/arena/');
    }
}

btn?.addEventListener('click', () => {
    getLocalSettings();
})
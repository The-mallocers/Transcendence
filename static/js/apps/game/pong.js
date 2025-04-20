import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from '../../spa/spa.js';
import {isGameOver} from "./VarGame.js"

const socket = WebSocketManager.gameSocket;
let canvas = document.getElementById("pongCanvas");
let ctx = canvas.getContext("2d");
let lusername = document.getElementById("lusername");
let rusername = document.getElementById("rusername");
let lscore = document.getElementById("scoreLeft");
let rscore = document.getElementById("scoreRight");

let height = 500;
const width = 1000;

const ballSize = 10;
const paddleThickness = 20;
let paddleHeight = 100;


canvas.width = width;
canvas.height = height;

lusername.innerHTML = window.GameState.left.username
rusername.innerHTML = window.GameState.right.username
console.log('meowmeowmeow', window.GameState)

socket.onmessage = (e) => {
    const jsonData = JSON.parse(e.data);
    console.log("received the message below");
    console.log(jsonData);
    console.log("received the message with Data");
    console.log(jsonData.data)
    if (jsonData.data) {
        console.log(jsonData.data.action)
    }

    //Attempt at handling errors
    if (jsonData.data.action == "EXCEPTION") {
        isGameOver.gameIsOver = true;
        WebSocketManager.closeGameSocket();
        navigateTo("/");
    }

    if (jsonData.event == "UPDATE") {

        if (jsonData.data.action == "PADDLE_LEFT_UPDATE") {
            window.GameState.left.y = jsonData.data.content.y
        } else if (jsonData.data.action == "PADDLE_RIGHT_UPDATE") {
            window.GameState.right.y = jsonData.data.content.y
        } else if (jsonData.data.action == "BALL_UPDATE") {
            window.GameState.ballX = jsonData.data.content.x;
            window.GameState.ballY = jsonData.data.content.y;
        } else if (jsonData.data.action == "SCORE_LEFT_UPDATE") {
            lscore.innerHTML = jsonData.data.content
        } else if (jsonData.data.action == "SCORE_RIGHT_UPDATE") {
            rscore.innerHTML = jsonData.data.content
        }
    } else if (jsonData.event == "ERROR") {
        console.log("WE GOT AN ERROR"); 
        if (jsonData.data.action == "OPPONENT_LEFT") {
            console.log("Opponent Disconnected");
            navigateTo("/pong/disconnect/"); 
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
        }
    } else if (jsonData.data.action == "GAME_ENDING") {
        const game_id = jsonData.data.content
        navigateTo(`/pong/gameover/?game=${game_id}`);
        isGameOver.gameIsOver = true;
        WebSocketManager.closeGameSocket();
    }
};


const keys = {};
const previous_keys = {};
let previous_direction = null;

window.addEventListener('keydown', (event) => {
    switch (event.key) {
        case 'ArrowUp':
            keys.up = true;
            break;
        case 'ArrowDown':
            keys.down = true;
            break;
    }
});

document.addEventListener('keyup', (event) => {
    switch (event.key) {
        case 'ArrowUp':
            keys.up = false;
            break;
        case 'ArrowDown':
            keys.down = false;
            break;
    }
});


function updatePaddles() {
    let direction = null;
    //This might look confusing, but this is to simulate strafing keys
    if (keys.up && keys.down) {
        if (previous_keys.up) {
            direction = 'down'
        } else if (previous_keys.down) {
            direction = 'up'
        }
    } else if (keys.up) {
        direction = 'up'
        previous_keys.up = true;
        previous_keys.down = false;
    } else if (keys.down) {
        direction = 'down'
        previous_keys.down = true;
        previous_keys.up = false;
    } else {
        direction = 'idle'
    }
    if (direction && direction !== previous_direction) {
        previous_direction = direction;
        const message = {
            "event": "game",
            "data": {
                "action": "paddle_move",
                "args": direction
            }
        }
        socket.send(JSON.stringify(message));
    }
}


const clearArena = () => {
    ctx.clearRect(0, 0, width, height);
};

const drawArena = () => {
    ctx.fillStyle = "#12141A";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "white";
    ctx.beginPath();
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.lineWidth = 1;
    ctx.stroke();
};

const drawPaddle = (x, y) => {
    ctx.fillStyle = "white";
    ctx.fillRect(x, y, paddleThickness, paddleHeight);
};

const drawBall = (x, y) => {
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(x, y, ballSize, 0, Math.PI * 2);
    ctx.fill();
};

const render = () => {
    clearArena();
    drawArena();
    drawPaddle(10, window.GameState.left.y);
    drawPaddle(width - paddleThickness - 10, window.GameState.right.y);
    drawBall(window.GameState.ballX, window.GameState.ballY);
};


render()

function gameLoop() {
    if (isGameOver.gameIsOver == true) {
        return;
    }
    updatePaddles();
    render();
    requestAnimationFrame(gameLoop);
}

isGameOver.gameIsOver = false;
if (isGameOver.gameIsOver == false) {
    requestAnimationFrame(gameLoop);
}

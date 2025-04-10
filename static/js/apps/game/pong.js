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
const paddleThickness = 10;
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
            console.log(jsonData.data.content.y)
            window.GameState.left.y = jsonData.data.content.y
        } else if (jsonData.data.action == "PADDLE_RIGHT_UPDATE") {
            window.GameState.right.y = jsonData.data.content.y
        } else if (jsonData.data.action == "BALL_UPDATE") {
            window.GameState.ballX = jsonData.data.content.x;
            window.GameState.ballY = jsonData.data.content.y;
            // console.table(jsonData.data.content.x, jsonData.data.content.y)
        } else if (jsonData.data.action == "SCORE_LEFT_UPDATE") {
            lscore.innerHTML = jsonData.data.content
        } else if (jsonData.data.action == "SCORE_RIGHT_UPDATE") {
            rscore.innerHTML = jsonData.data.content
        }
    } else if (jsonData.data.event == "ERROR") {
        if (jsonData.data.action == "OPPONENT_LEFT") {
            console.log("Opponent Disconnected");
            navigateTo("/"); //Later, Redirect to a screen telling your opponent he disconnected.
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
        }
    } else if (jsonData.data.action == "GAME_ENDING") {
        //Close socket here as well
        const game_id = jsonData.data.content
        console.log("game id is ", game_id);
        console.log("ALLO C FINI LA GAME");
        //We will want to navigate to a specific game
        console.log("Navigating to /pong/gameover/");
        navigateTo(`/pong/gameover/?game=${game_id}`);
        isGameOver.gameIsOver = true;
        WebSocketManager.closeGameSocket();
    }
    // return render()
    // })s
};


const keys = {
    'a': false,
    'd': false,
};

const previous_keys = {
    'a': false,
    'd': false,
}

document.addEventListener('keydown', (event) => {
    switch (event.key) {
        case 'ArrowUp':
            keys.up = true;
            break;
        case 'ArrowDown':
            keys.down = true;
            break;
    }
    // updatePaddles()
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
    // updatePaddles()
});

function updatePaddles() {
    // gauche
    let direction = null;
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
    if (direction) {
        // console.log("direction is :", direction)
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

// Complete rendering function
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
        // alert("returning like a fucking idiot")
        return;
    }
    // console.log("Im looping, ", game_is_over)
    updatePaddles();
    render();
    requestAnimationFrame(gameLoop);
}

// Start the game loop
isGameOver.gameIsOver = false;
if (isGameOver.gameIsOver == false) {
    // alert("I am in the loop for the first time")
    requestAnimationFrame(gameLoop);
}

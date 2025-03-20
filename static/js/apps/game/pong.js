import { WebSocketManager } from "../../websockets/websockets.js";
import { navigateTo } from '../../spa/spa.js';

const socket = WebSocketManager.gameSocket;
let canvas = document.getElementById("pongCanvas");
let ctx = canvas.getContext("2d");
let lnick = document.getElementById("lnick");
let rnick = document.getElementById("rnick");
let lscore = document.getElementById("scoreLeft");
let rscore = document.getElementById("scoreRight");

let height = 500;
const width = 1000;

const ballSize = 10;
const paddleThickness = 10;
let paddleHeight = 100;

canvas.width = width;
canvas.height = height;
let paddleDefaultPos = 250 - (paddleHeight / 2)

// window.GameState = {
//     ballX: width / 2,
//     ballY: height / 2,
//     leftPaddleY: paddleDefaultPos,
//     rightPaddleY: paddleDefaultPos
// };

lnick.innerHTML = window.GameState.left.nick
rnick.innerHTML = window.GameState.right.nick
console.log('meowmeowmeow', window.GameState)


socket.onmessage = (e) => {
    // queueMicrotask(() => {
    const jsonData = JSON.parse(e.data);
    console.log("VTGVTVYTHVYTFVYTFVYTVFYTRVYTRVBYT")
    console.log("87786guTV7B",jsonData)
    console.log(jsonData.data)
    if (jsonData.data) {
        console.log(jsonData.data.action)
    }

    if (jsonData.event == "UPDATE") {

        if (jsonData.data.action == "PADDLE_LEFT_UPDATE"){
            console.log(jsonData.data.content.y)
            window.GameState.left.y  = jsonData.data.content.y
        }
        else if (jsonData.data.action == "PADDLE_RIGHT_UPDATE"){
            window.GameState.right.y =  jsonData.data.content.y
        }
        else if (jsonData.data.action == "BALL_UPDATE") {
            window.GameState.ballX = jsonData.data.content.x;
            window.GameState.ballY = jsonData.data.content.y;
            // console.table(jsonData.data.content.x, jsonData.data.content.y)
        }
        else if (jsonData.data.action == "SCORE_LEFT_UPDATE"){
            lscore.innerHTML = jsonData.data.content
        }
        else if (jsonData.data.action == "SCORE_RIGHT_UPDATE"){
            rscore.innerHTML = jsonData.data.content
        }
        else if (jsonData.data.action == "ENDING"){
            navigateTo("/pong/gameover/");
        }
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

//A -> D
// A true D false -> D -> EN BAS

//0 - 0
//A - 0
//Update old keys
// A = true - D = false

//if A == true D == True

document.addEventListener('keydown', (event) => {
    switch(event.key) {
        case 'ArrowUp': keys.up = true; break;
        case 'ArrowDown': keys.down = true; break;
    }
    // updatePaddles()
});

document.addEventListener('keyup', (event) => {
    switch(event.key) {
        case 'ArrowUp': keys.up = false; break;
        case 'ArrowDown': keys.down = false; break;
    }
    // updatePaddles()
});

function updatePaddles() {
    // gauche
    let direction = null;
    if (keys.up && keys.down) {
        //I want to check the old key combination, and have the direction be
        //what the "new" direction is
        if (previous_keys.up) {
            direction = 'down'
        }
        else if (previous_keys.down) {
            direction = 'up'
        }
    }
    else if (keys.up) {
        direction = 'up'
        previous_keys.up = true;
        previous_keys.down = false;
    }
    else if (keys.down) {
        direction = 'down'
        previous_keys.down = true;
        previous_keys.up = false;
    }
    else {
        direction = 'idle'
    }
    if (direction) {
        console.log("direction is :", direction)
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

    ///////////////
    // updatePaddles()
    ///////////////
    drawPaddle(10, window.GameState.left.y);
    drawPaddle(width - paddleThickness - 10, window.GameState.right.y);
    drawBall(window.GameState.ballX, window.GameState.ballY);
};


/*{
    "event": "UPDATE",
    "data": {
        "action": "PADDLE_1_UPDATE",
        "content": {
            "width": 10.0,
            "height": 100.0,
            "x": 0.0,
            "y": -1.0,
            "speed": 10.0
        }
    }
}*/




// Animation loop
// function animationLoop() {
//     render();
//     requestAnimationFrame(animationLoop);
// }

// // Start the animation loop
// requestAnimationFrame(animationLoop);

// setInterval(render, 1);  // 60 fps


render()

function gameLoop() {
    updatePaddles();
    render();
    requestAnimationFrame(gameLoop);
}

// Start the game loop
requestAnimationFrame(gameLoop);

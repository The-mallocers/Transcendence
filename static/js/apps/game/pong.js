import { WebSocketManager } from "../../websockets/websockets.js";

const socket = WebSocketManager.gameSocket;

let canvas = document.getElementById("pongCanvas");
let ctx = canvas.getContext("2d");

let height = 500;
const width = 1000;

const ballSize = 10;
const paddleThickness = 10;
const paddleHeight = 100;

canvas.width = width;
canvas.height = height;

const paddleDefaultPos = 250

let GameState = {
    ballX: width / 2,
    ballY: height / 2,
    leftPaddleY: paddleDefaultPos,
    rightPaddleY: paddleDefaultPos
};


const keys = {
    'a': false,
    'd': false,
};

document.addEventListener('keydown', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = true; break;
        case 'd': keys.d = true; break;
    }
    // updatePaddles()
});

document.addEventListener('keyup', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = false; break;
        case 'd': keys.d = false; break;
    }
    // updatePaddles()
});

function updatePaddles() {
    // gauche
    let direction = null;
    if (keys.a) {
        direction = 'up'
    }
    else if (keys.d) {
        direction = 'down'
    }
    
    if (direction) {
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
    drawPaddle(10, GameState.leftPaddleY);
    drawPaddle(width - paddleThickness - 10, GameState.rightPaddleY);
    drawBall(GameState.ballX, GameState.ballY);
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


socket.onmessage = (e) => {
    // queueMicrotask(() => {
    const jsonData = JSON.parse(e.data);
    
    // console.log(jsonData)
    if (jsonData.event == "UPDATE") {

        if (jsonData.data.action == "PADDLE_1_UPDATE"){
            console.log(jsonData.data.content.y)
            GameState.leftPaddleY = paddleDefaultPos + jsonData.data.content.y
        }
        else if (jsonData.data.action == "PADDLE_2_UPDATE"){
            GameState.rightPaddleY =  paddleDefaultPos + jsonData.data.content.y
        }
        else if (jsonData.data.action == "BALL_UPDATE") {
            GameState.ballX = jsonData.data.content.x;
            GameState.ballY = jsonData.data.content.y;
            // console.table(jsonData.data.content.x, jsonData.data.content.y)
        }
    }
        // return render()
    // })s
};

// Animation loop
// function animationLoop() {
//     render();
//     requestAnimationFrame(animationLoop);
// }

// // Start the animation loop
// requestAnimationFrame(animationLoop);

// setInterval(render, 1);  // 60 fps



function gameLoop() {
    updatePaddles();
    render();
    requestAnimationFrame(gameLoop);
}

// Start the game loop
requestAnimationFrame(gameLoop);
import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from '../../spa/spa.js';
import {isGameOver} from "./VarGame.js";
import { tournamentData } from "./VarGame.js";
import { toast_message } from "../profile/toast.js";
// import { apiFriends } from "../profile/profile.js";

const socket = WebSocketManager.gameSocket;
let canvas = document.getElementById("pongCanvas");
let ctx = canvas.getContext("2d");
const lusername = document.getElementById("lusername");
const rusername = document.getElementById("rusername");
const lpicture = document.getElementById("lpicture");
const rpicture = document.getElementById("rpicture");
let lscore = document.getElementById("scoreLeft");
let rscore = document.getElementById("scoreRight");
let timer = document.getElementById("timer");

const height = 500;
const width = 1000;
const ballSize = 10;
const paddleThickness = 20;
const paddleHeight = 100;
canvas.width = width;
canvas.height = height;
const PADDLE_SPEED = 300; // pixels per second

let is_gameplay_start = false;
let last_time = 0;
let did_tab_out = false;
let delta = 0;
let frameCount = 0;
let left_last_move = "idle";
let right_last_move = "idle";

//Below code might be useful one day.
// const name_data = await apiFriends("/api/friends/whoami/");
// console.log("my name is", name_data);
// const my_name = name_data.data.username;

//Si un petit malin va sur la page sans raison
if (!socket || socket.readyState === WebSocket.CLOSED) {
    navigateTo("/");
    remove_toast();
    toast_message("You are being redirected because you are not in any game right now")
} else {
    tournamentData.gameIsReady = false;
    // console.log(window.GameState);
    lusername.innerHTML = window.GameState.left.username;
    rusername.innerHTML = window.GameState.right.username;
    // console.log("WHAT ARE THE URLS:");
    // console.log(window.GameState.left.picture);
    // console.log(window.GameState.right.picture);
    lpicture.src = window.GameState.left.picture;
    rpicture.src = window.GameState.right.picture;

    socket.onmessage = (e) => {
        const jsonData = JSON.parse(e.data);
        // console.log("received the message below");
        // console.log(jsonData);
        // console.log("received the message with Data");
        // console.log(jsonData.data)
        // if (jsonData.data) {
        //     console.log(jsonData.data.action)
        // }

        //Attempt at handling errors
        if (jsonData.data.action == "EXCEPTION") {
            // console.log("REDIRECTION BECAUSE EXCEPTION HAPPENED");
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
            navigateTo("/");
            remove_toast();
            toast_message("something went wrong, you are being redirected")
        }

        if (jsonData.data.action == "WAITING_TO_START") {
            is_gameplay_start = true
            timer.innerHTML = jsonData.data.content.timer;
        }

        if (jsonData.event == "UPDATE") {
            timer.remove()

            // if (is_gameplay_start == false) {
            //     is_gameplay_start = true;
            //     last_time = performance.now();
            // }
            if (jsonData.data.action == "PADDLE_LEFT_UPDATE") {
                // console.log("move from server:", jsonData.data.content.move);
                const current_move = jsonData.data.content.move
                if (current_move != left_last_move) {
                    window.GameState.left.y = jsonData.data.content.y;
                    left_last_move = current_move;
                }
            } else if (jsonData.data.action == "PADDLE_RIGHT_UPDATE") {
                // console.log("move from server:", jsonData.data.content.move);
                const current_move = jsonData.data.content.move
                if (current_move != right_last_move) {
                    window.GameState.right.y = jsonData.data.content.y
                    right_last_move = current_move;
                }
            } else if (jsonData.data.action == "BALL_UPDATE") {
                // console.log("Ball update is :", jsonData.data);
                //We only update if we changed direction, this makes things smoother.
                if (did_tab_out || window.GameState.balldy != jsonData.data.content.dy || window.GameState.balldx != jsonData.data.content.dx) {
                    did_tab_out = false;
                    window.GameState.ballX = jsonData.data.content.x;
                    window.GameState.ballY = jsonData.data.content.y;
                    window.GameState.balldy = jsonData.data.content.dy;
                    window.GameState.balldx = jsonData.data.content.dx;
                }
            } else if (jsonData.data.action == "SCORE_LEFT_UPDATE") {
                lscore.innerHTML = jsonData.data.content
            } else if (jsonData.data.action == "SCORE_RIGHT_UPDATE") {
                rscore.innerHTML = jsonData.data.content
            }
        } else if (jsonData.event == "ERROR") {
            if (jsonData.data.action == "OPPONENT_LEFT") {
                const game_id = jsonData.data.content
                console.log("Opponent Disconnected");
                navigateTo(`/pong/disconnect/?game=${game_id}`);
                isGameOver.gameIsOver = true;
                WebSocketManager.closeGameSocket();
            }
        } else if (jsonData.data.action == "GAME_ENDING") {
            const game_id = jsonData.data.content
            console.log("GAME IS OVER");
            //Hack that allows me to not change backend 
            //otherwise game over will navigate after we redirected to tournament.
            if (window.location.pathname != "/pong/tournament/tree/" ) {
                navigateTo(`/pong/gameover/?game=${game_id}`);
            }
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
        }
    };
}


document.addEventListener('visibilitychange', () => {
    did_tab_out = true;
    const isTabVisible = document.visibilityState === 'visible';

    if (isTabVisible) {
        last_time = performance.now();
    }
});

const keys = {};
const previous_keys = {};
let previous_direction = null;

document.addEventListener('keydown', (event) => {
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
            direction = 'down';
        } else if (previous_keys.down) {
            direction = 'up';
        }
    } else if (keys.up) {
        direction = 'up';
        previous_keys.up = true;
        previous_keys.down = false;
    } else if (keys.down) {
        direction = 'down';
        previous_keys.down = true;
        previous_keys.up = false;
    } else {
        direction = 'idle';
    }
    //the code below might be useful later, idk it doesnt work rn
    // if (my_name == lusername) {
    //     left_last_move = direction;
    // }
    // else if (my_name == rusername) {
    //     right_last_move = direction;
    // }
    // if (direction != previous_direction) {
    //     console.log("previous direction :", previous_direction);
    //     console.log("direction :", direction);
    // }
    // (direction && previous_direction != direction) || frameCount % 5 === 0
    if ((direction && previous_direction != direction) || frameCount % 5 === 0) { //Trying to send less updates
        previous_direction = direction;
        // console.log("Sending to server direction :", direction);
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

const drawBall = () => {
    const nextX = window.GameState.ballX + window.GameState.balldx * delta;
    const nextY = window.GameState.ballY + window.GameState.balldy * delta;

    const leftBoundary = 10; //This is harcoding, if im a real G Id do an api call to get that value.
    const rightBoundary = width - 10;

    if (nextX > leftBoundary && nextX < rightBoundary) {
        window.GameState.ballX = nextX;
        window.GameState.ballY = nextY;
    }

    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(window.GameState.ballX, window.GameState.ballY, ballSize, 0, Math.PI * 2);
    ctx.fill();
};


const render = () => {
    clearArena();
    drawArena();
    drawPaddles();
    drawBall();
};

function drawPaddles() {
    const left_next_y = window.GameState.left.y + computeSpeed(left_last_move) * delta;
    const right_next_y = window.GameState.right.y + computeSpeed(right_last_move) * delta;
    window.GameState.left.y = handleWallCollision(left_next_y);
    window.GameState.right.y = handleWallCollision(right_next_y);
    drawPaddle(10, window.GameState.left.y);
    drawPaddle(width - paddleThickness - 10, window.GameState.right.y);
}

function handleWallCollision(y) {
    if (y < 0) {
        return 0;
    } else if (y + paddleHeight > height) {
        return height - paddleHeight;
    } else {
        return y
    }
}


function computeSpeed(last_move) {
    let speed = 0;
    if (last_move == "up") {
        speed = -1 * PADDLE_SPEED;
    } else if (last_move == "down") {
        speed = PADDLE_SPEED;
    } else {
        speed = 0;
    }
    return speed;
}

function computeDelta() {
    const curr_time = performance.now();
    delta = (curr_time - last_time) / 1000;
    last_time = curr_time;
    return delta;
}

function gameLoop() {
    if (isGameOver.gameIsOver == true) {
        return;
    }
    frameCount++;
    computeDelta();
    updatePaddles();
    render();
    requestAnimationFrame(gameLoop);
}

const antibsbool = Boolean(
    socket &&
    socket.readyState !== WebSocket.CLOSED &&
    window.GameState &&
    window.GameState.left &&
    window.GameState.right
);

isGameOver.gameIsOver = false;
if (isGameOver.gameIsOver == false && antibsbool) {
    requestAnimationFrame(gameLoop);
}
//We used to call this to draw the ball once, maybe hardcore it in some other way, but ideally play an animation for the first few seconds.
if (antibsbool) {
    render();
}
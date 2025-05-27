import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from '../../spa/spa.js';
import {isGameOver, tournamentData} from "./VarGame.js";
import {remove_toast, toast_message} from "../profile/toast.js";
import { localState } from "./VarGame.js";
import { sanitizeHTML } from "../../utils/utils.js";
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
let btns = document.getElementById("btns");



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
// const my_name = name_data.data.username;
function makeBtns(){
    btns.innerHTML = `
        <div class="btn intra-btn" data-route="/pong/local/create/">play again</div>
        <div class="btn intra-btn" data-route="/pong/gamemodes/">quit</div>
    `
}

if (!socket || socket.readyState === WebSocket.CLOSED) {
    navigateTo("/");
    remove_toast();
    toast_message("Not in a game, redirecting");
} else {
    tournamentData.gameIsReady = false;

    lusername.innerHTML = sanitizeHTML(window.GameState.left.username);
    rusername.innerHTML = sanitizeHTML(window.GameState.right.username);

    lpicture.src = window.GameState.left.picture;
    if (!window.GameState.left.picture || window.GameState.left.picture === "") {
        lpicture.src = "/static/img/gallery/Dogs/cookedDog.png";
    }

    rpicture.src = window.GameState.right.picture;
    if (!window.GameState.right.picture || window.GameState.right.picture === "") {
        rpicture.src = "/static/img/gallery/Cats/mewingCat.png";
    }


    socket.onmessage = (e) => {
        const jsonData = JSON.parse(e.data);

        if (jsonData.data.action == "EXCEPTION") {

            isGameOver.gameIsOver = true;
            localState.gameIsLocal = false;
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

            if (jsonData.data.action == "PADDLE_LEFT_UPDATE") {
                const current_move = jsonData.data.content.move
                if (current_move != left_last_move) {
                    window.GameState.left.y = jsonData.data.content.y;
                    left_last_move = current_move;
                }
            } else if (jsonData.data.action == "PADDLE_RIGHT_UPDATE") {
                const current_move = jsonData.data.content.move
                if (current_move != right_last_move) {
                    window.GameState.right.y = jsonData.data.content.y
                    right_last_move = current_move;
                }
            } else if (jsonData.data.action == "BALL_UPDATE") {
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
                navigateTo(`/pong/disconnect/?game=${game_id}`);
                isGameOver.gameIsOver = true;
                localState.gameIsLocal = false;

                WebSocketManager.closeGameSocket();
            }
        } else if (jsonData.data.action == "GAME_ENDING") {
            const game_id = jsonData.data.content
            isGameOver.gameIsOver = true;
            WebSocketManager.closeGameSocket();
            if (localState.gameIsLocal) {
                localState.gameIsLocal = false;
                //Update window avec les noms et le score.
                window.local = {
                    left_name: lusername.innerText,
                    right_name: rusername.innerText,

                    left_score: lscore.innerText,
                    right_score: rscore.innerText,
                }
                navigateTo('/pong/local/gameover/');
                return
            }
            localState.gameIsLocal = false;
            //otherwise game over will navigate after we redirected to tournament.
            if (window.location.pathname != "/pong/tournament/tree/" ) {
                navigateTo(`/pong/gameover/?game=${game_id}`);
            }
        }
    };
}


document?.addEventListener('visibilitychange', () => {
    did_tab_out = true;
    const isTabVisible = document.visibilityState === 'visible';

    if (isTabVisible) {
        last_time = performance.now();
    }
});

const keys = {};
const previous_keys = {};
let previous_direction = null;

const keys_local = {};
const previous_keys_local = {};
let previous_direction_local = null;



document?.addEventListener('keydown', (event) => {
    switch (event.key) {
        case 'ArrowUp':
            keys.up = true;
            break;
        case 'ArrowDown':
            keys.down = true;
            break;
    }
});

document?.addEventListener('keyup', (event) => {
    switch (event.key) {
        case 'ArrowUp':
            keys.up = false;
            break;
        case 'ArrowDown':
            keys.down = false;
            break;
    }
});

function addLocalDown(event) {
    const key = event.key.toLowerCase();
    switch (key) {
        case 'w':
            keys_local.up = true;
            break;
        case 's':
            keys_local.down = true;
            break;
    }
}

function addLocalUp(event) {
    const key = event.key.toLowerCase();
    switch (key) {
        case 'w':
            keys_local.up = false;
            break;
        case 's':
            keys_local.down = false;
            break;
    }
}


if (localState.gameIsLocal == true) {
    document?.addEventListener('keyup', addLocalUp);
    document?.addEventListener('keydown', addLocalDown);
}


function updateLocalPaddles() {
    let direction = null;
    //This might look confusing, but this is to simulate strafing key   s
    if (keys_local.up && keys_local.down) {
        if (previous_keys_local.up) {
            direction = 'down';
        } else if (previous_keys_local.down) {
            direction = 'up';
        }
    } else if (keys_local.up) {
        direction = 'up';
        previous_keys_local.up = true;
        previous_keys_local.down = false;
    } else if (keys_local.down) {
        direction = 'down';
        previous_keys_local.down = true;
        previous_keys_local.up = false;
    } else { direction = 'idle';}
    if ((direction && previous_direction != direction) || frameCount % 5 === 0) { //Trying to send less updates
        previous_direction_local = direction;
        const message = {
            "event": "game",
            "data": {
                "action": "paddle_move",
                "args": {
                    "move": direction,
                    "side": "left"
                }
            }
        }
        socket.send(JSON.stringify(message));
    }
}

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
    } else { direction = 'idle';}
    if ((direction && previous_direction != direction) || frameCount % 5 === 0) { //Trying to send less updates
        previous_direction = direction;
        const message = {
            "event": "game",
            "data": {
                "action": "paddle_move",
                "args": {
                    "move": direction,
                    "side": "right"
                }
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
    if (localState.gameIsLocal == true) { updateLocalPaddles()};
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

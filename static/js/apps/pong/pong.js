// Create WebSocket connection
const socket = new WebSocket('ws://' + window.location.host + '/ws/game/58d755a781fa4e9cb8e3e3c21fe90714/');

let p1_id = "fe1ff7d694404e94982b27ca0c15c50b"
let p2_id = "3020e19d34764eb6ad792aeb6ff3e791"

let paddle_p1 = null;
let paddle_p2 = null;
let ball = null;
let p1_score = 0;
let p2_score = 0;

// Get the canvas context
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

function joinGameP1() {
    socket.send(JSON.stringify({
        action: 'join_game',
        player_id: p1_id
    }));
}

function joinGameP2() {
    socket.send(JSON.stringify({
        action: 'join_game',
        player_id: p2_id
    }));
}

function startGame() {
    socket.send(JSON.stringify({
        action: 'start_game',
        player_id: p1_id
    }));
}

document.getElementById('play_btn_p1').addEventListener('click', joinGameP1);
document.getElementById('play_btn_p2').addEventListener('click', joinGameP2);
document.getElementById('start_game').addEventListener('click', startGame);

// Handle messages from server
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log(data)

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (data.type === 'paddle_move') {
        const id = data.player.id.toString().trim();  // Assurez-vous que c'est bien une chaîne
        if (id === p1_id)
            paddle_p1 = data.player.paddle
        if (id === p2_id)
            paddle_p2 = data.player.paddle
        drawGame()
    }
    if (data.type === 'ball_update') {
        ball = data.ball;
        drawGame()
    }
    if (data.type === 'p1_score_update') {
        p1_score = data.score
        drawGame()
    }
    if (data.type === 'p2_score_update') {
        p2_score = data.score
        drawGame()
    }

};

socket.onopen = function() {
    console.log('WebSocket connection established!');
};

// Gérer la fermeture de la connexion
socket.onclose = function(event) {
    console.log('WebSocket connection closed', event);
};

function drawGame() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    ctx.fillStyle = 'black';
    ctx.fillRect(25, paddle_p1.y, 10, 100);
    ctx.fillRect(canvas.width - 25, paddle_p2.y, 10, 100);

    // Draw ball
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, 10, 0, Math.PI * 2);
    ctx.fill();

    // Draw scores
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(p1_score, 100, 50);
    ctx.fillText(p2_score, canvas.width - 100, 50);
}

const keys = {
    'a': false,
    'd': false,
    'j': false,
    'l': false,
};

document.addEventListener('keydown', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = true; break;
        case 'd': keys.d = true; break;
        case 'j': keys.j = true; break;
        case 'l': keys.l = true; break;
    }
});

document.addEventListener('keyup', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = false; break;
        case 'd': keys.d = false; break;
        case 'j': keys.j = false; break;
        case 'l': keys.l = false; break;
    }
});

function updatePaddles() {
    // gauche
    if (keys.a) socket.send(JSON.stringify({action: 'paddle_move', player_id: p1_id, direction: 'up'}));
    if (keys.d) socket.send(JSON.stringify({action: 'paddle_move', player_id: p1_id, direction: 'down'}));
    // droite
    if (keys.j) socket.send(JSON.stringify({action: 'paddle_move', player_id: p2_id, direction: 'down'}));
    if (keys.l) socket.send(JSON.stringify({action: 'paddle_move', player_id: p2_id, direction: 'up'}));
}

setInterval(updatePaddles, 1000/60);  // 60 fps
// Create WebSocket connection
const socket = new WebSocket('ws://' + window.location.host + '/ws/game/e7162f47d1be4f8a8054de6b71e0a4ea/');

let p1_id = "312db8136bde45119dc4d837c16fed80"
let p2_id = "6ac386bcd4f1473892c58d50fd567589"

let paddle_p1 = null;
let paddle_p2 = null;

// Get the canvas context
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

function sendMessageP1() {
    socket.send(JSON.stringify({
        action: 'join_game',
        player_id: p1_id
    }));
}

function sendMessageP2() {
    socket.send(JSON.stringify({
        action: 'join_game',
        player_id: p2_id
    }));
}

document.getElementById('play_btn_p1').addEventListener('click', sendMessageP1);
document.getElementById('play_btn_p2').addEventListener('click', sendMessageP2);

// Handle messages from server
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    // console.log("I have received a game update")
    if (data.success === 'paddle_move') {
        // console.log("I have received a legit game update")
        const id = data.player.id.toString().trim();  // Assurez-vous que c'est bien une chaîne
        if (id === p1_id)
            paddle_p1 = data.player.paddle
        if (id === p2_id)
            paddle_p2 = data.player.paddle
        drawGame();
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
    // if (!paddle_p1) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    ctx.fillStyle = 'black';
    ctx.fillRect(25, paddle_p1.y, 10, 100);
    ctx.fillRect(canvas.width - 25, paddle_p2.y, 10, 100);

    // Draw ball
    // ctx.beginPath();
    // ctx.arc(gameState.ball_x, gameState.ball_y, 10, 0, Math.PI * 2);
    // ctx.fill();

    // Draw scores
    // ctx.font = '24px Arial';
    // ctx.textAlign = 'center';
    // ctx.fillText(gameState.left_score, 100, 50);
    // ctx.fillText(gameState.right_score, canvas.width - 100, 50);
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
    if (keys.a) socket.send(JSON.stringify({action: 'paddle_move', player_id: '312db8136bde45119dc4d837c16fed80', direction: 'up'}));
    if (keys.d) socket.send(JSON.stringify({action: 'paddle_move', player_id: '312db8136bde45119dc4d837c16fed80', direction: 'down'}));
    if (keys.j) socket.send(JSON.stringify({action: 'paddle_move', player_id: '6ac386bcd4f1473892c58d50fd567589', direction: 'down'}));
    if (keys.l) socket.send(JSON.stringify({action: 'paddle_move', player_id: '6ac386bcd4f1473892c58d50fd567589', direction: 'up'}));
}

setInterval(updatePaddles, 1000/60);  // 60 fps
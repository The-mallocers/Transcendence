// Create WebSocket connection
const socket = new WebSocket('ws://' + window.location.host + '/ws/somepath/');

// Get the canvas context
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// Game state will be updated from server
let gameState = null;

// Handle messages from server
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log("I have received a game update")
    if (data.type === 'game_state_update') {
        console.log("I have received a legit game update")
        gameState = data.state;
        drawGame();
    }
};

function drawGame() {
    if (!gameState) return;

    console.log("hello")
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    ctx.fillStyle = 'black';
    ctx.fillRect(25, gameState.left_paddle_y, 10, 100);
    ctx.fillRect(canvas.width - 25, gameState.right_paddle_y, 10, 100);

    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball_x, gameState.ball_y, 10, 0, Math.PI * 2);
    ctx.fill();

    // Draw scores
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(gameState.left_score, 100, 50);
    ctx.fillText(gameState.right_score, canvas.width - 100, 50);
}

const keys = {
    'a': false,
    'd': false,
    'j': false,
    'l': false
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
    if (keys.a) socket.send(JSON.stringify({type: 'paddle_move', paddle: 'left', direction: 'up'}));
    if (keys.d) socket.send(JSON.stringify({type: 'paddle_move', paddle: 'left', direction: 'down'}));
    if (keys.j) socket.send(JSON.stringify({type: 'paddle_move', paddle: 'right', direction: 'down'}));
    if (keys.l) socket.send(JSON.stringify({type: 'paddle_move', paddle: 'right', direction: 'up'}));
}

setInterval(updatePaddles, 1000/60);  // 60 fps
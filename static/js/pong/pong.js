// Create WebSocket connection
const socket = new WebSocket('ws://' + window.location.host + '/ws/somepath/');

// Get the canvas context
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// Game state will be updated from server
let gameState = null;

// Handle keyboard input
document.addEventListener('keypress', function (event) {
    let data = null;

    switch (event.key.toLowerCase()) {
        case 'a':
            data = {paddle: 'left', direction: 'up'};
            break;
        case 'd':
            data = {paddle: 'left', direction: 'down'};
            break;
        case 'j':
            data = {paddle: 'right', direction: 'down'};
            break;
        case 'l':
            data = {paddle: 'right', direction: 'up'};
            break;
    }

    if (data) {
        socket.send(JSON.stringify({
            type: 'paddle_move',
            ...data
        }));
    }
});

// Handle messages from server
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.type === 'game_state_update') {
        gameState = data.state;
        drawGame();
    }
};

function drawGame() {
    if (!gameState) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    ctx.fillStyle = 'black';
    // Top paddle
    ctx.fillRect(gameState.top_paddle_x, 0, 100, 10);
    // Bottom paddle
    ctx.fillRect(gameState.bottom_paddle_x, canvas.height - 10, 100, 10);

    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball_x, gameState.ball_y, 10, 0, Math.PI * 2);
    ctx.fill();

    // Draw scores
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(gameState.top_score, canvas.width / 2, 50);
    ctx.fillText(gameState.bottom_score, canvas.width / 2, canvas.height - 30);
}
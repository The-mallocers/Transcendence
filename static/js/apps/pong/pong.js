import { WebSocketManager } from "../../websockets/websockets.js"

let paddle_p1 = JSON.parse({"y": 0});
let paddle_p2 = JSON.parse({"y": 0});
let ball = {x: 0, y: 0};
let p1_score = 0;
let p2_score = 0;
let is_active = 0;

// Get the canvas context
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// Handle messages from server
const PongGame = () => {
    
    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log(data)

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (data.type === 'paddle_move') {
            const id = data.player.id.toString().trim();  // Assurez-vous que c'est bien une chaîne
            console.log("id: " + id + "\np1: " + p1_id + "\np2: " + p2_id)
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
        if (data.action === 'The game has ended') {
            p2_score = data.score
            drawGame()
        }

    };
}

PongGame(clientId);

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
};

document.addEventListener('keydown', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = true; break;
        case 'd': keys.d = true; break;
    }
});

document.addEventListener('keyup', (event) => {
    switch(event.key.toLowerCase()) {
        case 'a': keys.a = false; break;
        case 'd': keys.d = false; break;
    }
});

function updatePaddles() {
    // gauche
    if (keys.a) socket.send(JSON.stringify({type: 'paddle_move', player_id: p1_id, direction: 'up'}));
    if (keys.d) socket.send(JSON.stringify({type: 'paddle_move', player_id: p1_id, direction: 'down'}));
}

setInterval(updatePaddles, 1000/60);  // 60 fps
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

let GameState = {
    ballX: width / 2,
    ballY: height / 2,
    leftPaddleY: height / 4,
    rightPaddleY: height / 6
};

// Performance monitoring
let lastFrameTime = performance.now();
let frameCount = 0;
let fps = 0;

// WebSocket monitoring
let messageCount = 0;
let messagesPerSecond = 0;
let lastMessageTime = performance.now();
let messageGaps = [];  // Track time between messages
let lastMessageTimestamp = 0;

// Batch detection
let batchCount = 0;
let batchSizes = [];
let currentBatchSize = 0;
let batchThreshold = 50; // ms - if messages arrive closer than this, they're in a "batch"

// Debug data storage for graphing/analysis
let debugData = {
    messageTimes: [],
    renderTimes: [],
    ballPositions: []
};

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

// Extended debug info
const drawDebugInfo = () => {
    ctx.fillStyle = "yellow";
    ctx.font = "12px Arial";
    ctx.fillText(`Render FPS: ${fps.toFixed(1)}`, 10, 20);
    ctx.fillText(`WebSocket msgs/sec: ${messagesPerSecond.toFixed(1)}`, 10, 40);
    
    // Batch information
    const avgBatchSize = batchSizes.length > 0 
        ? batchSizes.reduce((a, b) => a + b, 0) / batchSizes.length 
        : 0;
    ctx.fillText(`Batches detected: ${batchCount}`, 10, 60);
    ctx.fillText(`Avg batch size: ${avgBatchSize.toFixed(1)} messages`, 10, 80);
    
    // Message timing
    const avgGap = messageGaps.length > 0 
        ? messageGaps.reduce((a, b) => a + b, 0) / messageGaps.length 
        : 0;
    ctx.fillText(`Avg message gap: ${avgGap.toFixed(0)}ms`, 10, 100);
    ctx.fillText(`Ball: (${GameState.ballX.toFixed(1)}, ${GameState.ballY.toFixed(1)})`, 10, 120);
    
    // Show current batch status
    if (performance.now() - lastMessageTime < 100) {
        ctx.fillStyle = "red";
        ctx.fillText("RECEIVING BATCH NOW", 10, 140);
    }
};

// Complete rendering function
const render = () => {
    const renderStart = performance.now();
    
    clearArena();
    drawArena();
    drawPaddle(10, GameState.leftPaddleY);
    drawPaddle(width - paddleThickness - 10, GameState.rightPaddleY);
    drawBall(GameState.ballX, GameState.ballY);
    drawDebugInfo();
    
    // Store render timing data
    debugData.renderTimes.push({
        time: renderStart,
        duration: performance.now() - renderStart
    });
    
    // Update FPS counter
    frameCount++;
    const now = performance.now();
    if (now - lastFrameTime >= 1000) {
        fps = frameCount * 1000 / (now - lastFrameTime);
        frameCount = 0;
        lastFrameTime = now;
        
        // Clean up old debug data (keep last 5 seconds)
        const cutoffTime = now - 5000;
        debugData.messageTimes = debugData.messageTimes.filter(item => item.time > cutoffTime);
        debugData.renderTimes = debugData.renderTimes.filter(item => item.time > cutoffTime);
        debugData.ballPositions = debugData.ballPositions.filter(item => item.time > cutoffTime);
        
        // Reset batch detection after logging
        if (messageGaps.length > 100) {
            messageGaps = messageGaps.slice(-100);
        }
        if (batchSizes.length > 20) {
            batchSizes = batchSizes.slice(-20);
        }
    }
};

// Track WebSocket message patterns
socket.onmessage = (e) => {
    const receiveTime = performance.now();
    const jsonData = JSON.parse(e.data);
    
    // Track message timing
    messageCount++;
    
    // Calculate time since last message
    const timeSinceLastMessage = lastMessageTimestamp > 0 ? receiveTime - lastMessageTimestamp : 0;
    if (lastMessageTimestamp > 0) {
        messageGaps.push(timeSinceLastMessage);
        
        // Batch detection
        if (timeSinceLastMessage < batchThreshold) {
            // Part of a batch
            currentBatchSize++;
        } else if (currentBatchSize > 0) {
            // End of a batch
            batchSizes.push(currentBatchSize);
            batchCount++;
            currentBatchSize = 1; // This message starts a new potential batch
        } else {
            // Isolated message
            currentBatchSize = 1;
        }
    } else {
        currentBatchSize = 1;
    }
    
    lastMessageTimestamp = receiveTime;
    
    // Store message timing data
    debugData.messageTimes.push({
        time: receiveTime,
        gap: timeSinceLastMessage
    });
    
    // Update message rate counter
    const now = performance.now();
    if (now - lastMessageTime >= 1000) {
        messagesPerSecond = messageCount * 1000 / (now - lastMessageTime);
        messageCount = 0;
        lastMessageTime = now;
    } else {
        lastMessageTime = now; // Update last message time
    }
    
    if (jsonData.event == "UPDATE") {
        if (jsonData.data.action == "BALL_UPDATE") {
            GameState.ballX = jsonData.data.content.x;
            GameState.ballY = jsonData.data.content.y;
            
            // Store ball position data
            debugData.ballPositions.push({
                time: receiveTime,
                x: GameState.ballX,
                y: GameState.ballY
            });
        }
    }
};

// Print detailed batch analysis to console every 5 seconds
setInterval(() => {
    console.log(`--- WebSocket Message Analysis ---`);
    console.log(`Messages per second: ${messagesPerSecond.toFixed(1)}`);
    
    // Analyze gaps to identify patterns
    if (messageGaps.length > 0) {
        const sortedGaps = [...messageGaps].sort((a, b) => a - b);
        const minGap = sortedGaps[0];
        const maxGap = sortedGaps[sortedGaps.length - 1];
        const medianGap = sortedGaps[Math.floor(sortedGaps.length / 2)];
        
        console.log(`Message timing: min=${minGap.toFixed(0)}ms, median=${medianGap.toFixed(0)}ms, max=${maxGap.toFixed(0)}ms`);
        
        // Look for clusters in the gaps
        const clusters = {};
        for (const gap of messageGaps) {
            // Round to nearest 50ms
            const bucket = Math.round(gap / 50) * 50;
            clusters[bucket] = (clusters[bucket] || 0) + 1;
        }
        
        console.log("Gap distribution:");
        Object.entries(clusters)
            .sort(([a], [b]) => parseInt(a) - parseInt(b))
            .forEach(([bucket, count]) => {
                console.log(`  ${bucket}ms: ${'#'.repeat(Math.min(count, 40))}`);
            });
    }
    
    if (batchSizes.length > 0) {
        console.log(`Batches detected: ${batchCount}`);
        console.log(`Average batch size: ${(batchSizes.reduce((a, b) => a + b, 0) / batchSizes.length).toFixed(1)} messages`);
    }
    
    console.log("----------------------------");
}, 5000);

// Animation loop
function animationLoop() {
    render();
    requestAnimationFrame(animationLoop);
}

// Start the animation loop
requestAnimationFrame(animationLoop);
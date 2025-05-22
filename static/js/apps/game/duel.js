import { navigateTo } from "../../spa/spa.js";
import { WebSocketManager } from "../../websockets/websockets.js";
import { toast_message } from "../profile/toast.js"; 
import { remove_toast } from "../profile/toast.js";
import { getClientId } from "../../utils/utils.js";

let clientId;
let gameStartingInProcess = false;

const images = await getImages();
if(images){
    const player1Image = document.querySelector('.player-photo.client');
    const player2Image = document.querySelector('.player-photo.opponent');
    const newPlayer1ImageUrl = images.hostPicture; 
    const newPlayer2ImageUrl = images.opponentPicture;
    player1Image.src = newPlayer1ImageUrl;
    player2Image.src = newPlayer2ImageUrl;
}

clientId = await getClientId();
const gameSocket = await WebSocketManager.initGameSocket(clientId);
const notifSocket = WebSocketManager.notifSocket;

const cancelDuel = document.querySelector(".cancel-duel");
if (cancelDuel) {
    cancelDuel.addEventListener('click', function (event) {
        navigateTo('/pong/gamemodes/')
    })
}

const opponentDiv = document.querySelector(".opponent_player");
if (opponentDiv) {
    const urlParams = new URLSearchParams(window.location.search);
    const opponentName = urlParams.get("opponent");
    opponentDiv.innerHTML = opponentName;
}

let height = 500;
const width = 1000;

const paddleHeight = 100;

let paddleDefaultPos = 250 - (paddleHeight / 2)

window.GameState = {
    ballY: height / 2,
    ballX: width / 2,

    left: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: "",
        id: ""
    },
    right: {
        x: paddleDefaultPos,
        y: paddleDefaultPos,
        username: "",
        id: ""
    }
}

window.GameInfos = {
    left: {}
}

const startGameMessage = {
    "event": "game",
    "data": {
        "action": "start_game"
    }
}

notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);

    if (message.data.action == "DUEL_REFUSED") {
        navigateTo("/pong/gamemodes/");
        remove_toast();
        toast_message(`${message.data.content.username} refuses the duel`);
    } else if (message.data.action == "DUEL_JOIN") {
        const pendingDiv = document.querySelector(".state-of-player");
        if (pendingDiv) {
            pendingDiv.innerHTML = "join";
            pendingDiv.style.backgroundColor = "#00babc";
            pendingDiv.style.color = "white"
        }
    } else if (message.data.action == "DUEL_CREATED") {
        navigateTo(`/pong/duel/?opponent=${message.data.content.opponent}`);
    }
    else if(message.data.action == "BLOCKED_USER"){ 
        remove_toast();
        toast_message("You have blocked this user");
        navigateTo('');
    }
}

gameSocket.onmessage = (e) => {
    const jsonData = JSON.parse(e.data);

    console.log(jsonData.data.action);

    // Handle player info first to ensure we have the data
    if (jsonData.data.action == "PLAYER_INFOS") {
        console.log("PLAYER INFOS IS:")
        console.log(jsonData.data.content)
        window.GameState = {
            ballY: height / 2,
            ballX: width / 2,
            started: false,

            left: {
                x: jsonData.data.content.left.paddle.x,
                y: jsonData.data.content.left.paddle.y,
                username: jsonData.data.content.left.username,
                id: jsonData.data.content.left.client_id || "",
                picture: jsonData.data.content.left.player_profile
            },
            right: {
                x: jsonData.data.content.right.paddle.x,
                y: jsonData.data.content.right.paddle.y,
                username: jsonData.data.content.right.username,
                id: jsonData.data.content.right.client_id || "",
                picture: jsonData.data.content.right.player_profile
            }
        }
    }

    // Modify the STARTING handler to use a flag
    else if (jsonData.data.action == "STARTING") {
        if (!gameStartingInProcess) {
            gameStartingInProcess = true;
            console.log("Game starting - sending start message");
            // Do NOT navigate until the correct time
            gameSocket.send(JSON.stringify(startGameMessage));
        }
    }

    // Handle the waiting to start message to show the countdown
    else if (jsonData.data.action === "WAITING_TO_START") {
        const timer = jsonData.data.content.timer;
        console.log("Game starting in", timer);
        
        // Update the timer in the UI
        const timerElement = document.getElementById("timer");
        if (timerElement) {
            timerElement.textContent = timer;
        }
        
        // Navigate to arena when timer is at 5 (beginning of countdown)
        if (timer === 5 && !window.location.pathname.includes("arena")) {
            console.log("Navigating to arena");
            navigateTo("/pong/arena/");
        }
    }
};

async function getImages(){
    const urlParams = new URLSearchParams(window.location.search);
    const opponentName = urlParams.get("opponent");
    try {
        const response = await fetch(`/api/friends/get_duels_images/?opponent=${opponentName}`, {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        if (data.status == "success") {
            const images = data.data;
            const duelExist = data.data.duelExist;
            if(!duelExist)
                navigateTo("/pong/gamemodes/");
            return images;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        navigateTo("/pong/gamemodes/")
        // console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

import { navigateTo } from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"

let client_id = null;
const clientId = await getClientId()
const gameSocket = WebSocketManager.initGameSocket(clientId);

const urlParams = new URLSearchParams(window.location.search);
const targetUsername = urlParams.get('target');
console.log("Target username:", targetUsername);
const opponent = document.querySelector(".opponent_player")
if (opponent)
{
    opponent.innerHTML = targetUsername;
}

gameSocket.onmessage = (event) => {

}

async function getClientId() {
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();

        if (data.client_id) {
            client_id = data.client_id;
            return client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

function create_message_duel(action, targetUser)
{
    let message = {
        "event": "game",
        "data": {
            "action": action,
            "args": {
                "target": targetUser,
            }
        } 
    }
    return message;
}
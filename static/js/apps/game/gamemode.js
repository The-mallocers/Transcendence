import { navigateTo } from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"

let client_id;
const clientId= await getClientId();
const gameSocket = await WebSocketManager.initGameSocket(clientId);

window.choose_duel_friend = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = function(){
    const button = document.querySelector(".duel_friend");
    // const username = button.getAttribute('data-username');
    const usernameID = button.getAttribute('data-id');
    const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
    modal.hide();
    const message = create_message_duel("create_duel", usernameID)
    gameSocket.send(JSON.stringify(message));
}

gameSocket.onmessage = (event) =>{
    console.log(event.data);
    const message = JSON.parse(event.data);
    if(message.data.action == "DUEL_CREATED")
    {
        navigateTo('/pong/duel/');
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

export {gameSocket};
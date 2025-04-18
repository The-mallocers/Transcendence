import { navigateTo } from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"

let client_id;
// const clientId= await getClientId();
let gameSocket;

window.choose_duel_friend = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = async function(){
    try{
        const button = document.querySelector(".duel_friend");
        // const username = button.getAttribute('data-username');
        const usernameID = button.getAttribute('data-id');
        const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
        modal.hide();
        // const message = create_message_duel("create_duel", usernameID);
        // // gameSocket = await WebSocketManager.initGameSocket(clientId);
        // if (!gameSocket) {
        //     console.log("Socket not initialized, initializing now...");
        //     await initialize();
        // }
        
        // // Check readyState before sending (0: CONNECTING, 1: OPEN, 2: CLOSING, 3: CLOSED)
        // if (gameSocket.readyState !== 1) {
        //     console.error("WebSocket is not open, current state:", gameSocket.readyState);
        //     return;
        // }
        // gameSocket.send(JSON.stringify(message));
        navigateTo('/pong/duel/?creator');
    }
    catch(error){
        console.log(error);
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

async function initialize() {
    try {
        client_id = await getClientId();
        
        // Only initialize the socket once
        if (!gameSocket && client_id) {
            gameSocket = await WebSocketManager.initGameSocket(client_id);
            
            // Set up message handler
            gameSocket.onmessage = (event) => {
                console.log("Received:", event.data);
                try {
                    const message = JSON.parse(event.data);
                    if (message.data && message.data.action === "DUEL_CREATED") {
                        navigateTo('/pong/duel/');
                    }
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                }
            };
            
            gameSocket.onerror = (error) => {
                console.error("WebSocket error:", error);
            };
            
            console.log("WebSocket initialized successfully");
        }
    } catch (error) {
        console.error("Initialization error:", error);
    }
}

// async function getClientId() {
//     try {
//         const response = await fetch("/api/auth/getId/", {
//             method: "GET",
//             credentials: "include",
//         });
//         const data = await response.json();

//         if (data.client_id) {
//             client_id = data.client_id;
//             return client_id;
//         } else {
//             throw new Error(data.error);
//         }
//     } catch (error) {
//         console.error("Erreur lors de la récupération de l'ID :", error);
//         return null;
//     }
// }

export {gameSocket};
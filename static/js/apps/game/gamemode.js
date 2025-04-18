import { navigateTo } from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"
import { notifSocket } from "../profile/profile.js";

window.choose_duel_friend = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = async function(){
    try{
        const button = document.querySelector(".duel_friend");
        const usernameID = button.getAttribute('data-id');
        const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
        modal.hide();
        const message = create_message_duel("create_duel", usernameID);
        notifSocket.send(JSON.stringify(message));
        navigateTo('/pong/duel/');
    }
    catch(error){
        console.log(error);
    }
}

function create_message_duel(action, targetUser)
{
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "target": targetUser,
            }
        } 
    }
    return message;
}
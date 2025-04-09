import { WebSocketManager } from "../../websockets/websockets.js";
import { navigateTo } from "../../spa/spa.js";

window.choose_duel_friend = function()
{
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.launch_duel = function(){
    console.log("c'est le fight");
    
}
import { navigateTo } from "../../spa/spa.js";
import {WebSocketManager} from "../../websockets/websockets.js"
import { notifSocket } from "../profile/profile.js";
import { create_message_notif } from "../profile/profile.js";

window.choose_duel_friend = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = function(){
    const button = document.querySelector(".duel_friend");
    const username = button.getAttribute('data-username');
    const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
    modal.hide();
    const message = create_message_notif("ask_duel", username)
    notifSocket.send(JSON.stringify(message));
    navigateTo(`/pong/duel/?target=${username}`);
}


import { navigateTo } from "../../spa/spa.js";

window.choose_duel_friend = function()
{
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = function(){
    const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
    modal.hide();
    navigateTo("/pong/duel");
}
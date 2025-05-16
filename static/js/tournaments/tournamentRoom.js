import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
const leave_btn = document.querySelector("#leave-btn");

import {apiFriends} from "../profile/profile.js";
import {WebSocketManager} from "../../websockets/websockets.js";

const pathname = window.location.pathname;
console.log(pathname);
const notifSocket = WebSocketManager.notifSocket;
console.log(notifSocket);

if (pathname == "/pong/tournament/") {
    console.log("tournament room");
    const friends = await apiFriends("/api/friends/get_friends/");
    const duelFriends = document.querySelector(".friends-to-duel");
    console.log(friends);
    if (!friends.length) {
        const parser = new DOMParser();
        const html =
            `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>No friend to duel</div>
        </li>`
        const doc = parser.parseFromString(html, "text/html");
        const friendElement = doc.body.firstChild;
        duelFriends.appendChild(friendElement);
    }
    friends.forEach(friend => {
        const parser = new DOMParser();
        const html =
            `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${friend.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green duel_friend me-4">Duel</button>
            </div>
        </li>`
        const doc = parser.parseFromString(html, "text/html");
        const friendElement = doc.body.firstChild;
        const duelButton = friendElement.querySelector('.duel_friend');
        duelButton.addEventListener('click', function () {
            hide_modal(friend.id)
        });
        duelFriends.appendChild(friendElement);
    });
}

function leaveTournament() {
    WebSocketManager.closeTournamentSocket();
    navigateTo("/pong/gamemodes/");
}

delete_btn?.addEventListener('click', ()=>{
    leaveTournament();
});

leave_btn?.addEventListener('click', ()=>{
    leaveTournament();
});

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }    
}

window.invite_friends = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = async function (usernameId) {
    try {
        const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
        modal.hide();
        // const message = create_message_duel("create_duel", usernameId);
        // notifSocket.send(JSON.stringify(message));
    } catch (error) {
        console.log(error);
    }
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));



import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";
import { apiFriends } from "../apps/profile/profile.js";
import { remove_toast, toast_message } from "../apps/profile/toast.js";

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
// const leave_btn = document.querySelector("#leave-btn");

const leave_tournament = {
    "event": "tournament",
    "data": {
        "action": "leave_tournament"
    }
}

function leaveTournament() {
    WebSocketManager.tournamentSocket.send(JSON.stringify(leave_tournament))
    // WebSocketManager.closeTournamentSocket();
    navigateTo("/pong/gamemodes/");
}

delete_btn?.addEventListener('click', ()=>{
    leaveTournament();
});

// leave_btn.addEventListener('click', ()=>{
//     leaveTournament();
// });

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));

window.invite_friends = async function() {
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    await populateFriendsModal();
    friendSelectionModal.show();
}

async function populateFriendsModal() {
    const friends = await apiFriends("/api/friends/get_friends/");
    const inviteFriends = document.querySelector(".friends-to-invite");
    
    inviteFriends.innerHTML = '';
    
    if (!friends.length) {
        const parser = new DOMParser();
        const html =
            `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>No friends to invite</div>
        </li>`
        const doc = parser.parseFromString(html, "text/html");
        const friendElement = doc.body.firstChild;
        inviteFriends.appendChild(friendElement);
    } else {
        friends.forEach(friend => {
            const parser = new DOMParser();
            const html =
                `<li class="list-group-item d-flex justify-content-between align-items-center">
                <div>${friend.username}</div>
                <div class="d-flex align-items-center">
                    <button type="button" class="type-intra-green invite_friend me-4">Invite</button>
                </div>
            </li>`
            const doc = parser.parseFromString(html, "text/html");
            const friendElement = doc.body.firstChild;
            const inviteButton = friendElement.querySelector('.invite_friend');
            inviteButton.addEventListener('click', function () {
                sendInvitation(friend.id);
            });
            inviteFriends.appendChild(friendElement);
        });
    }
}

function sendInvitation(friendId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
    modal.hide();
    
    console.log(`Invitation sent to friend with ID: ${friendId}`);
    const inviteMessage = {
        "event": "tournament",
        "data": {
            "action": "invite_friend",
            "args": {
                "friend_id": friendId
            }
        }
    };
    tournamentSocket.send(JSON.stringify(inviteMessage));
    
    // Show invitation sent feedback
    remove_toast();
    toast_message("Invitation sent", "success");
}
            
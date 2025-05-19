import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";
import { apiFriends } from "../apps/profile/profile.js";

const tournamentSocket = WebSocketManager.tournamentSocket;
const delete_btn = document.querySelector("#delete-btn");
const leave_btn = document.querySelector("#leave-btn");


function leaveTournament() {
    const message = {
        "event": "tournament",
        "data": {
            "action": "leave_tournament"
        }
    };
    tournamentSocket.send(JSON.stringify(message));
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
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.innerHTML = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Tournament Invitation</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                Invitation sent!
            </div>
        </div>
    `;
    document.body.appendChild(toastContainer);
    
    const toastElement = toastContainer.querySelector('.toast');
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();
    
    // Remove toast container after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}

// Listen for tournament socket messages
tournamentSocket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.event === "TOURNAMENT") {
        const action = message.data.action;
        
        if (action === "TOURNAMENT_INVITATION_SENT") {
            console.log(`Invitation sent to ${message.data.content.target_name}`);
        }
    }
};



import { navigateTo } from "../../spa/spa.js";
import { notifSocket } from "../profile/profile.js";
import { apiFriends } from "../profile/profile.js";

const pathname = window.location.pathname;
console.log(pathname);

if(pathname == "/pong/gamemodes/")
{
    const friends = await apiFriends("/api/friends/get_friends/");
    const duelFriends = document.querySelector(".friends-to-duel");
    friends.forEach(friend => {
        console.log(friend);
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
        duelButton.addEventListener('click', function() {
            hide_modal(friend.id)
        });
        duelFriends.appendChild(friendElement);
    });
}
window.choose_duel_friend = function(){
    const friendSelectionModal = new bootstrap.Modal(document.querySelector('#friendSelectionModal'));
    friendSelectionModal.show();
}

window.hide_modal = async function(usernameId){
    try{
        const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
        modal.hide();
        const message = create_message_duel("create_duel",usernameId);
        notifSocket.send(JSON.stringify(message));
        // navigateTo('/pong/duel/');
    }
    catch(error){
        console.log(error);
    }
}

export function create_message_duel(action, targetUser)
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
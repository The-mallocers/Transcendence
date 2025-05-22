import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from "../../spa/spa.js";
import { toast_friend } from "./toast.js";
import { toast_duel } from "./toast.js";
import { toast_message } from "./toast.js";
import { toast_tournament } from "./toast.js";
import { remove_toast } from "./toast.js";
import { create_front_chat_room } from "../../utils/utils.js";

const notifSocket = WebSocketManager.notifSocket;

const searchParams = new URLSearchParams(window.location.search);
const pathname = window.location.pathname;
// console.log(pathname);

if (!searchParams.has('username') && pathname == '/') {
    const friends_group = document.querySelector('.friends_group');
    const pending_group = document.querySelector('.pending_group');
    
    if (friends_group) {
        const existingButtons = friends_group.querySelectorAll('button.friendrequest');
        friends_group.innerHTML = '';
        existingButtons.forEach(button => friends_group.appendChild(button));
    }
    
    if (pending_group) {
        pending_group.innerHTML = '';
    }
    
    // Display all friends and pending friends
    const friends = await apiFriends("/api/friends/get_friends/");
    const pending_friends = await apiFriends("/api/friends/get_pending_friends/");
    const pending_duels = await apiFriends("/api/friends/get_pending_duels/");
    const friends_online_status = JSON.parse(document.getElementById('friends-data')?.textContent);
    const pending_tournament_invitations = JSON.parse(document.getElementById('pending-tournament-invitations-data')?.textContent || '[]');

    friends.forEach(friend => {
        // Check if this friend is already in the list
        if (document.getElementById(`friend-${friend.username.replace(/\s+/g, '-')}`)) {
            return; // Skip this friend if already added
        }

        const friends_group = document.querySelector('.friends_group');
        const parser = new DOMParser();
        const status = friends_online_status[friend.username];
        console.log("status:", status);
        const html_friend =
            `<li id="friend-${friend.username.replace(/\s+/g, '-')}" class="list-group-item d-flex justify-content-between align-items-center">
            <div>${friend.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green delete_friend me-4" >delete</button>
                <div id=${friend.username}_status >${status}</div>
            </div>
        </li>`
        const doc = parser.parseFromString(html_friend, "text/html");
        const friendElement = doc.body.firstChild;

        const deleteButton = friendElement.querySelector('.delete_friend');
        deleteButton.addEventListener('click', function () {
            friendElement.remove();
            handleDeleteFriend(friend.username);
        });
        friends_group.appendChild(friendElement);
    });

    pending_friends.forEach(pending_friend => {
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const html_string =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
                    ${pending_friend.username}
                    <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                        <button type="button" class="type-intra-green accept_friend">accept</button>
                        <button type="button" class="type-intra-white refuse_friend">refuse</button>
                    </div>
                </li>
                `
        const doc = parser.parseFromString(html_string, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptButton = pendingElement.querySelector('.accept_friend');
        acceptButton.addEventListener('click', function () {
            pendingElement.remove();
            handleAcceptFriend(pending_friend.username);
        });

        const deleteButton = pendingElement.querySelector('.refuse_friend');
        deleteButton.addEventListener('click', function () {
            pendingElement.remove();
            handleRefuseFriend(pending_friend.username);
        });
        pending_group.appendChild(pendingElement);
    });
    pending_duels.forEach((duel) => {
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const html_string =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
                    ${duel.username} wants to duel
                    <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                        <button type="button" class="type-intra-green accept_duel">accept</button>
                        <button type="button" class="type-intra-white refuse_duel">refuse</button>
                    </div>
                </li>
                `
        const doc = parser.parseFromString(html_string, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptButton = pendingElement.querySelector('.accept_duel');
        acceptButton.addEventListener('click', function () {
            const parentListItem = this.closest('li.pending_item');
            if (parentListItem) {
                parentListItem.remove();
            }
            console.log(duel.duel_id)
            handleAcceptDuel(duel.duel_id, duel.username);
        });

        const deleteButton = pendingElement.querySelector('.refuse_duel');
        deleteButton.addEventListener('click', function () {
            const parentListItem = this.closest('li.pending_item');
            if (parentListItem) {
                parentListItem.remove();
            }
            handleRefuseDuel(duel.duel_id, duel.username);
        });
        pending_group.appendChild(pendingElement);
    })
    pending_tournament_invitations.forEach((invitation) => {
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const html_string =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
                ${invitation.inviter_username} invites you to join tournament: ${invitation.tournament_name}
                <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                    <button type="button" class="type-intra-green accept_tournament" data-tournament-code="${invitation.tournament_code}" data-inviter="${invitation.inviter_username}">accept</button>
                    <button type="button" class="type-intra-white refuse_tournament" data-tournament-code="${invitation.tournament_code}" data-inviter="${invitation.inviter_username}">refuse</button>
                </div>
            </li>
            `
        const doc = parser.parseFromString(html_string, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptButton = pendingElement.querySelector('.accept_tournament');
        acceptButton.addEventListener('click', function () {
            pendingElement.remove();
            handleAcceptTour(invitation.tournament_code, invitation.inviter_username);
        });

        const deleteButton = pendingElement.querySelector('.refuse_tournament');
        deleteButton.addEventListener('click', function () {
            pendingElement.remove();
            handleRefuseTour(invitation.tournament_code, invitation.inviter_username);
        });
        
        if (pending_group) {
            pending_group.appendChild(pendingElement);
        }
    });
}

notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);

    if (message.data.action == "SESSION_EXPIRED") {
        remove_toast();
        toast_message("Session expired");
        navigateTo('/auth/login');
    }
    
    if(message.data.action == "ACK_SEND_FRIEND_REQUEST") {
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const htmlString =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
        ${message.data.content.username}
        <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
        <button type="button" class="type-intra-green accept_friend">accept</button>
        <button type="button" class="type-intra-white refuse_friend">refuse</button>
        </div>
        </li>
        `
        const doc = parser.parseFromString(htmlString, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptButton = pendingElement.querySelector('.accept_friend');
        acceptButton.addEventListener('click', function () {
            pendingElement.remove();
            handleAcceptFriend(message.data.content.username);
        });

        const deleteButton = pendingElement.querySelector('.refuse_friend');
        deleteButton.addEventListener('click', function () {
            pendingElement.remove();
            handleRefuseFriend(message.data.content.username);
        });
        if (pending_group) {
            pending_group.appendChild(pendingElement);
        }
        remove_toast();
        toast_friend(`New friend request from ${message.data.content.username}`, message.data, pendingElement);
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST" || message.data.action == "ACK_ACCEPT_FRIEND_REQUEST") {
        create_front_chat_room(message.data.content.room,
            message.data.content.username, 
            message.data.content.sender, 
            "Block",
            message.data.content.profile_picture);
        const friends_group = document.querySelector('.friends_group');
        const friend_duel = document.querySelector(".friends-to-duel");
        if(friends_group)
        {
            const parser = new DOMParser();
            const add_to_friend = 
            `<li class="list-group-item d-flex justify-content-between align-items-center">
                <div>${message.data.content.username}</div>
                <div class="d-flex align-items-center">
                    <button type="button" class="type-intra-green delete_friend me-4">delete</button>
                </div>
            </li>`
            const doc = parser.parseFromString(add_to_friend, "text/html");
            const friendElement = doc.body.firstChild;

            const deleteButton = friendElement.querySelector('.delete_friend');
            deleteButton.addEventListener('click', function () {
                friendElement.remove();
                handleDeleteFriend(message.data.content.username);
            });
            friends_group.appendChild(friendElement);
        }
        else if(friend_duel){
            const noFriendButton = friend_duel.querySelector(".no-friends-to-duel");
            if(noFriendButton)
                noFriendButton.remove();
            const parser = new DOMParser();
            const html =
                `<li class="list-group-item d-flex justify-content-between align-items-center">
                <div>${message.data.content.username}</div>
                <div class="d-flex align-items-center">
                    <button type="button" class="type-intra-green duel_friend me-4">Duel</button>
                </div>
            </li>`
            const doc = parser.parseFromString(html, "text/html");
            const friendElement = doc.body.firstChild;
            const duelButton = friendElement.querySelector('.duel_friend');
            duelButton.addEventListener('click', function () {
                hide_modal(message.data.content.sender)
            });
            friend_duel.appendChild(friendElement);
        }
    }
    else if(message.data.action == "ACK_DELETE_FRIEND") {
        const friendElements = document.querySelectorAll('.friends_group li');
        const duelElements = document.querySelectorAll('.friends-to-duel li');
        friendElements.forEach(elem => {
            const usernameElement = elem.querySelector('div:first-child');
            if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
                elem.remove();
            }
        });
        duelElements.forEach(elem => {
            const usernameElement = elem.querySelector('div:first-child');
            if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
                elem.remove();
            }
        });
        
        const chatElement = document.querySelector(`.chat-${message.data.content.username}`);
        if(chatElement)
            chatElement.parentElement.remove();
    }
    else if(message.data.action == "ACK_ASK_DUEL") {
        console.log("dans handle l'opponent vaut: " + message.data.content.username);
        let pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const htmlString =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
        ${message.data.content.username} wants to duel
        <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
        <button type="button" class="type-intra-green accept_duel">accept</button>
        <button type="button" class="type-intra-white refuse_duel">refuse</button>
        </div>
        </li>
        `
        const doc = parser.parseFromString(htmlString, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptDuel = pendingElement.querySelector('.accept_duel');
        acceptDuel.addEventListener('click', function () {
            handleAcceptDuel(message.data.content.code, message.data.content.username);
        });
        const refuseDuel = pendingElement.querySelector('.refuse_duel');
        refuseDuel.addEventListener('click', function () {
            pendingElement.remove();
            handleRefuseDuel(message.data.content.code, message.data.content.username);
        });
        if (pending_group) {
            pending_group.appendChild(pendingElement);
        }
        remove_toast();
        toast_duel(`${message.data.content.username} wants a duel`, message.data, pendingElement);
    } else if (message.data.action == "DUEL_CREATED") {
        navigateTo(`/pong/duel/?opponent=${message.data.content.opponent}`);
    }
    else if(message.data.action == "DUEL_NOT_EXIST")
    {
        remove_toast();
        
        navigateTo("/")
        toast_message("DUEL don't exist");
    } else if (message.data.action == "DUEL_REFUSED") {
        navigateTo("/pong/gamemodes/");
        remove_toast();
        toast_message(`${message.data.content.username} refuses the duel`);
    }
    else if(message.data.action == "USER_OFFLINE"){
        remove_toast();

        navigateTo('/pong/gamemodes/')
        toast_message(`Player you want to duel is offline`);
    } else if (message.data.action == "ACK_ONLINE_STATUS") {
        //TODO, Loop over the friend list and update the status of a friend if the username is a friend.
        const username = message.data.content.username;
        const online = message.data.content.online;
        const status = document.getElementById("online-status");
        if (status == null) {
            return;
        } //Woopsie !
        const query_username = searchParams.get("username");
        const friend_div = document.getElementById(`${username}_status`);
        // console.log(`the username is ${username}`);
        // console.log(`the combo is ${username}_status`);
        // console.log("Hello I got a message, friend div is", friend_div);
        if (friend_div) {
            if (online == true) {
                friend_div.innerHTML = "Online";
            } else {
                friend_div.innerHTML = "Offline";
            }
            return;
        }
        if (pathname == '/') {
            status.innerHTML = "Online";
            return;
        }
        if (username != query_username) {
            return;
        } //in theory useless but im afraid to delete it
        if (online == true) {
            status.innerHTML = "Online";
        } else {
            status.innerHTML = "Offline";
        }
    }
    else if(message.data.action == "BLOCKED_USER"){ 
        remove_toast();
        toast_message("You have blocked this user");
        navigateTo('');
    }
    else if(message.data.action == "TOURNAMENT_INVITATION"){
        const tournament_code = message.data.content.tournament_code;
        const inviter_username = message.data.content.username;
        const tournament_name = message.data.content.tournament_name;
        const itemToDelete = document.querySelector(`.pending_item`);
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const htmlString =
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center">
        ${message.data.content.username} invites you to join the tournament: ${tournament_name}
        <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end" role="group" aria-label="Basic example">
        <button type="button" class="type-intra-green accept_tournament" data-tournament-code="${tournament_code}" data-inviter="${inviter_username}">accept</button>
        <button type="button" class="type-intra-white refuse_tournament" data-tournament-code="${tournament_code}" data-inviter="${inviter_username}">refuse</button>
        </div>
        </li>
        `
        const doc = parser.parseFromString(htmlString, "text/html");
        const pendingElement = doc.body.firstChild;

        const acceptButton = pendingElement.querySelector('.accept_tournament');
        acceptButton.addEventListener('click', function () {
            pendingElement.remove();
            console.log(`accepting tournament ${message.data.content.tournament_code}`);
            handleAcceptTour(tournament_code, inviter_username);
        });

        const deleteButton = pendingElement.querySelector('.refuse_tournament');
        deleteButton.addEventListener('click', function () {
            pendingElement.remove();
            handleRefuseTour(tournament_code, inviter_username);
        });
        if (pending_group) {
            pending_group.appendChild(pendingElement);
        }
        remove_toast();
        toast_tournament(`You have been invited to ${tournament_name} by ${inviter_username}`, message.data, itemToDelete);
    }
    else if(message.data.action == "TOURNAMENT_INVITATION_ACCEPTED"){
        navigateTo(`/pong/tournament/?code=${message.data.content.tournament_code}`);
    }
};

window.handleAskFriend = function(username) {
    console.log("the friend to add is " + username);
    const message = create_message_notif("send_friend_request", username);
    notifSocket.send(JSON.stringify(message));
    navigateTo('/');
};

window.handleAcceptFriend = function(username) {
    remove_toast();
    const message = create_message_notif("accept_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleRefuseFriend = function(username) {
    remove_toast();
    const message = create_message_notif("refuse_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleDeleteFriend = function(username) {
    const message = create_message_notif("delete_friend", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleAcceptDuel = function(code, targetName) {
    remove_toast();
    const message = create_message_duel("accept_duel", code, targetName);
    notifSocket.send(JSON.stringify(message));
    navigateTo(`/pong/duel/?opponent=${targetName}`);
};

window.handleRefuseDuel = function(code, targetName) {
    remove_toast();
    const message = create_message_duel("refuse_duel", code, targetName);
    notifSocket.send(JSON.stringify(message));
};

window.handleAcceptTour = function(tournamentCode, inviterUsername) {
    remove_toast();
    const message = {
        "event": "notification",
        "data": {
            "action": "tournament_invitation_response",
            "args": {
                "tournament_code": tournamentCode,
                "inviter_username": inviterUsername,
                "action": "accept"
            }
        }
    };
    notifSocket.send(JSON.stringify(message));
    navigateTo(`/pong/tournament/?code=${tournamentCode}`);
}

window.handleRefuseTour = function(tournamentCode, inviterUsername) {
    remove_toast();

    const message = {
        "event": "notification",
        "data": {
            "action": "tournament_invitation_response",
            "args": {
                "tournament_code": tournamentCode,
                "inviter_username": inviterUsername,
                "action": "reject"
            }
        }
    };
    notifSocket.send(JSON.stringify(message));
    
    const pendingItem = document.querySelector(`.pending_item:has(button[data-tournament-code="${tournamentCode}"])`);
    if (pendingItem) {
        pendingItem.remove();
    }
}


window.handleAcceptTournamentInvitation = function(tournamentCode, inviterUsername) {
    remove_toast();
    const message = {
        "event": "notification",
        "data": {
            "action": "tournament_invitation_response",
            "args": {
                "tournament_code": tournamentCode,
                "inviter_username": inviterUsername,
                "action": "accept"
            }
        }
    };
    notifSocket.send(JSON.stringify(message));
};

window.handleRejectTournamentInvitation = function(tournamentCode, inviterUsername) {
    remove_toast();
    const message = {
        "event": "notification",
        "data": {
            "action": "tournament_invitation_response",
            "args": {
                "tournament_code": tournamentCode,
                "inviter_username": inviterUsername,
                "action": "reject"
            }
        }
    };
    notifSocket.send(JSON.stringify(message));
    
    const pendingItems = document.querySelectorAll('.pending_item');
    pendingItems.forEach(item => {
        const text = item.textContent;
        if (text.includes(inviterUsername) && text.includes('tournament')) {
            item.remove();
        }
    });
}

window.hide_modal = async function (usernameId) {
    try {
        const modal = bootstrap.Modal.getInstance(document.getElementById('friendSelectionModal'));
        modal.hide();
        const message = create_message_duel("create_duel", usernameId);
        notifSocket.send(JSON.stringify(message));
    } catch (error) {
        console.log(error);
    }
}

function create_message_notif(action, targetUser)
{
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "target_name": targetUser,
            }
        } 
    }
    return message;
}

function create_message_duel(action, code, targetName) {
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "code": code,
                "username": targetName,
            }
        }
    }
    return message;
}

function create_message_notif_block(action, targetUser, status) {
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "target_name": targetUser,
                "status": status,
            }
        }
    }
    return message;
}

export async function apiFriends(endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        if (data) {
            return data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

export {create_message_notif}
export {create_message_notif_block}
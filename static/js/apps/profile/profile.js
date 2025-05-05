import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from "../../spa/spa.js";
import { toast_friend } from "./toast.js";
import { toast_duel } from "./toast.js";
import { toast_message } from "./toast.js";
import { getClientId } from "../../utils/utils.js";

let client_id = null;
const clientId = await getClientId();
const notifSocket =  WebSocketManager.notifSocket; //Our notif socket is already loaded !


const searchParams = new URLSearchParams(window.location.search);
const pathname = window.location.pathname;
console.log(pathname);

if(!searchParams.has('username') && pathname == '/')
{
    // Display all friends and pending friends
    console.log("displaying friends from profile.js");
    const friends = await apiFriends("/api/friends/get_friends/");
    const pending_friends = await apiFriends("/api/friends/get_pending_friends/");
    const pending_duels = await apiFriends("/api/friends/get_pending_duels/");
    const friends_online_status = JSON.parse(document.getElementById('friends-data')?.textContent);
    
    friends.forEach(friend => {
        const friends_group = document.querySelector('.friends_group');
        const parser = new DOMParser();
        const status = friends_online_status[friend.username];
        console.log("status:", status);
        const html_friend = 
        `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${friend.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green delete_friend me-4" >delete</button>
                <div id=${friend.username}_status >${status}</div>
            </div>
        </li>`
        const doc = parser.parseFromString(html_friend, "text/html");
        const friendElement = doc.body.firstChild;
    
        const deleteButton = friendElement.querySelector('.delete_friend');
        deleteButton.addEventListener('click', function() {
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
        acceptButton.addEventListener('click', function() {
            pendingElement.remove();
            handleAcceptFriend(pending_friend.username);
        });
        
        const deleteButton = pendingElement.querySelector('.refuse_friend');
        deleteButton.addEventListener('click', function() {
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
        acceptButton.addEventListener('click', function() {
            const parentListItem = this.closest('li.pending_item');
            if (parentListItem) {
                parentListItem.remove();
            }
            console.log(duel.duel_id)
            handleAcceptDuel(duel.duel_id);
        });
        
        const deleteButton = pendingElement.querySelector('.refuse_duel');
        deleteButton.addEventListener('click', function() {
            const parentListItem = this.closest('li.pending_item');
            if (parentListItem) {
                parentListItem.remove();
            }
            handleRefuseDuel(duel.duel_id);
        });
        pending_group.appendChild(pendingElement);        
    })
}

notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);
    
    if(message.data.action == "ACK_SEND_FRIEND_REQUEST") {
        const pending_group = document.querySelector('.pending_group');
        if(pending_group)
        {
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
            acceptButton.addEventListener('click', function(){
                pendingElement.remove();
                handleAcceptFriend(message.data.content.username);
            });
            
            const deleteButton = pendingElement.querySelector('.refuse_friend');
            deleteButton.addEventListener('click', function() {
                pendingElement.remove();
                handleRefuseFriend(message.data.content.username);
            });
            pending_group.appendChild(pendingElement);
            toast_friend(`New friend request from ${message.data.content.username}`, message.data, pendingElement);
        }
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST" || message.data.action == "ACK_ACCEPT_FRIEND_REQUEST") {
        let friends_group = document.querySelector('.friends_group');
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
            deleteButton.addEventListener('click', function() {
                friendElement.remove();
                handleDeleteFriend(message.data.content.username);
            });
            friends_group.appendChild(friendElement);
        }
    }
    else if(message.data.action == "ACK_REFUSE_FRIEND_REQUEST") {
        // const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
        // if(buttonToDelete)
        // {
        //     buttonToDelete.remove();
        // }
    }
    else if(message.data.action == "ACK_DELETE_FRIEND_HOST") {
        // const friendElements = document.querySelectorAll('.friends_group li');
        // friendElements.forEach(elem => {
        //     const usernameElement = elem.querySelector('div:first-child');
        //     if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
        //         elem.remove();
        //     }
        // });
    }
    else if(message.data.action == "ACK_DELETE_FRIEND") {
        const friendElements = document.querySelectorAll('.friends_group li');
        friendElements.forEach(elem => {
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
        let pending_group = document.querySelector('.pending_group');
        if(pending_group)
        {
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
            acceptDuel.addEventListener('click', function() {
                handleAcceptDuel(message.data.content.code);
            });
            const refuseDuel = pendingElement.querySelector('.refuse_duel');
            refuseDuel.addEventListener('click', function() {
                pendingElement.remove();
                handleRefuseDuel(message.data.content.code);
            });
            pending_group.appendChild(pendingElement);
            toast_duel(`${message.data.content.username} wants a duel`, message.data, pendingElement);
        }
    }
    else if(message.data.action == "REFUSED_DUEL")
    {
        // const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
        // if(buttonToDelete)
        // {
        //     buttonToDelete.remove();
        // }
    }
    else if(message.data.action == "DUEL_REFUSED"){
        navigateTo("/pong/gamemodes/");
        toast_message(`${message.data.content.username} refuses the duel`);
    }
    else if(message.data.action == "ACK_ONLINE_STATUS") {
        //TODO, Loop over the friend list and update the status of a friend if the username is a friend.
        const username =  message.data.content.username;
        const online = message.data.content.online;
        const status = document.getElementById("online-status");
        if (status == null) {return ;} //Woopsie !
        const query_username = searchParams.get("username");
        const friend_div = document.getElementById(`${username}_status`);
        // console.log(`the username is ${username}`);
        // console.log(`the combo is ${username}_status`);
        // console.log("Hello I got a message, friend div is", friend_div);
        if (friend_div) {
            if (online == true) {
                friend_div.innerHTML = "Online";
            }
            else {
                friend_div.innerHTML = "Offline";
            }
            return ;
        }
        if (pathname == '/') {
            status.innerHTML = "Online";
            return ;
        }
        if (username != query_username) {return;} //in theory useless but im afraid to delete it
        if (online == true) {
            status.innerHTML = "Online";
        }
        else {
            status.innerHTML = "Offline";
        }
    }
}

//This file is now in utils.js ! 

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

// Define the functions in the global scope (window)
window.handleAskFriend = function(username) {
    console.log("the friend to add is " + username);
    const message = create_message_notif("send_friend_request", username);
    notifSocket.send(JSON.stringify(message));
    navigateTo('/');
};

window.handleAcceptFriend = function(username) {
    const toast = document.querySelector(".toast");
    
    if(toast)
        toast.remove();
    const message = create_message_notif("accept_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleRefuseFriend = function(username) {
    const toast = document.querySelector(".toast");
    if(toast)
        toast.remove();
    const message = create_message_notif("refuse_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleDeleteFriend = function(username) {
    const message = create_message_notif("delete_friend", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleAcceptDuel = function(code) {
    const toast = document.querySelector(".toast");
    
    if(toast)
        toast.remove();
    const message = create_message_duel("accept_duel", code);
    notifSocket.send(JSON.stringify(message));
    navigateTo('/pong/duel/');
};

window.handleRefuseDuel = function(code) {
    const toast = document.querySelector(".toast");
    
    if(toast)
        toast.remove();
    const message = create_message_duel("refuse_duel", code);
    notifSocket.send(JSON.stringify(message));
};

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

function create_message_duel(action, code)
{
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "code": code,
            }
        } 
    }
    return message;
}

function create_message_notif_block(action, targetUser, status)
{
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "target_name": targetUser,
                "status" : status,
            }
        } 
    }
    return message;
}

export async function apiFriends(endpoint) {
    console.log("Getting client ID")
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
        // console.error("Wesh je touche pas a ca mais on a pas de route api getAllFriends Chef")
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

export {notifSocket};
export {create_message_notif};
export {create_message_notif_block};
// export {getClientId}
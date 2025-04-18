import {WebSocketManager} from "../../websockets/websockets.js";
import {navigateTo} from "../../spa/spa.js";

let client_id = null;
const clientId = await getClientId();
const notifSocket =  await WebSocketManager.initNotifSocket(clientId);
const searchParams = new URLSearchParams(window.location.search);

if(!searchParams.has('username'))
{
    // Display all friends and pending friends
    console.log("displaying friends from profile.js");
    const friends = await apiFriends("/api/friends/get_friends/");
    const pending_friends = await apiFriends("/api/friends/get_pending_friends/")
    
    friends.forEach(friend => {
        const friends_group = document.querySelector('.friends_group');
        const parser = new DOMParser();
        const html_friend = 
        `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${friend.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green delete_friend me-4" >delete</button>
            </div>
        </li>
        `
        const doc = parser.parseFromString(html_friend, "text/html");
        const friendElement = doc.body.firstChild;
    
        const deleteButton = friendElement.querySelector('.delete_friend');
        deleteButton.addEventListener('click', () => {
            handleDeleteFriend(friend);
        });
        friends_group.appendChild(friendElement);
    });
    
    pending_friends.forEach(pending_friend => {
        const pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const html_string = 
                `<li class="list-group-item pending_item d-flex justify-content-between align-items-center" id="${pending_friend.username}">
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
        acceptButton.addEventListener('click', () => {
            handleAcceptFriend(pending_friend.username);
        });
        
        const deleteButton = pendingElement.querySelector('.refuse_friend');
        deleteButton.addEventListener('click', () => {
            handleRefuseFriend(pending_friend.username);
        });
        pending_group.appendChild(pendingElement);
    });
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
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center" id="${message.data.content.username}">
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
            acceptButton.addEventListener('click', () => {
                handleAcceptFriend(message.data.content.username);
            });
            
            const deleteButton = pendingElement.querySelector('.refuse_friend');
            deleteButton.addEventListener('click', () => {
                handleRefuseFriend(message.data.content.username);
            });
            pending_group.appendChild(pendingElement);
        }
        toasts(`New friend request from ${message.data.content.username}`, message.data);
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST") {
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
            deleteButton.addEventListener('click', () => {
                handleDeleteFriend(message.data.content.username);
            });
            friends_group.appendChild(friendElement);
            
            const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
            if(buttonToDelete)
            {
                buttonToDelete.remove();
            }
        }
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST") {
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
            </li>
            `
            const doc = parser.parseFromString(add_to_friend, "text/html");
            const friendElement = doc.body.firstChild;

            const deleteButton = friendElement.querySelector('.delete_friend');
            deleteButton.addEventListener('click', () => {
                handleDeleteFriend(message.data.content.username);
            });
            friends_group.appendChild(friendElement);
        }
        const newChat = document.querySelector('.chatRooms');
        if(newChat)
        {
            const parser = new DOMParser();
            const htmlChat = 
            `<button id="${message.data.content.room}" class="roomroom chat-${message.data.content.username} container d-flex align-items-center gap-3">
                    <img src="/static/assets/imgs/profile/default.png">
                    <div>${message.data.content.username}</div>
            </button>`
            console.log(htmlChat);
            const doc = parser.parseFromString(htmlChat, "text/html");
            const chatElement = doc.body.firstChild;
            newChat.appendChild(chatElement);
        }
    }
    else if(message.data.action == "ACK_REFUSE_FRIEND_REQUEST") {
        const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
        if(buttonToDelete)
        {
            buttonToDelete.remove();
        }
    }
    else if(message.data.action == "ACK_DELETE_FRIEND_HOST") {
        const friendElements = document.querySelectorAll('.friends_group li');
        friendElements.forEach(elem => {
            const usernameElement = elem.querySelector('div:first-child');
            if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
                elem.remove();
            }
        });
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
            chatElement.remove();
    }
    else if(message.data.action == "ACK_ASK_DUEL") {
        let pending_group = document.querySelector('.pending_group');
        if(pending_group)
        {
            const parser = new DOMParser();
            const htmlString = 
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center" id="${message.data.content.username}">
                ${message.data.content.username} wants to duel
                <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                    <button type="button" class="type-intra-green accept_duel" id="${message.data.content.sender}">accept</button>
                    <button type="button" class="type-intra-white delete_duel" onclick="handleRefuseDuel(this.dataset.username)">refuse</button>
                </div>
            </li>
            `
            
            const doc = parser.parseFromString(htmlString, "text/html");
            const pendingElement = doc.body.firstChild;

            const acceptDuel = pendingElement.querySelector('.accept_duel');
            acceptDuel.addEventListener('click', () => {
                handleAcceptDuel(message.data.content.code);
            });
            // const deleteDuel = pendingElement.querySelector('.delete_duel');
            // deleteDuel.addEventListener('click', () => {
            //     handleDeleteDuel(message.data.content.code);
            // });
            pending_group.appendChild(pendingElement);
        }
        toasts(`${message.data.content.username} wants a duel`, message.data);
    }
}

async function getClientId() {
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();

        if (data.client_id) {
            client_id = data.client_id;
            return client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

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

window.handleDeleteFriend = function(friend) {
    console.log(friend);
    const message = create_message_notif("delete_friend", friend.username);
    notifSocket.send(JSON.stringify(message));
};

window.handleAcceptDuel = function(code) {
    const message = {
        "event": "notification",
        "data": {
            "action": "accept_duel",
            "args": {
                "code": code,
            }
        } 
    }
    notifSocket.send(JSON.stringify(message));
    navigateTo(`/pong/duel/?guest=guest`);
};

window.handleRefuseDuel = function(username) {
    const message = create_message_notif("delete_friend", username);
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

function toasts(message, data){
    const date = new Date();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const time = `${hours}:${minutes}`;
    
    const toastHtml = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <img src="/static/assets/imgs/chat.png" class="rounded me-2" alt="..." style="width: 20px; height: 20px; object-fit: contain;">
            <strong class="me-auto">Friend Notification</strong>
            <small>${time}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
        <div class="mt-2 pt-2 border-top d-flex justify-content-end">
            <button type="button" class="btn type-intra-green me-2" onclick="handleAcceptFriend(this.dataset.username)" data-username=${data.content.username}>Accept</button>
            <button type="button" class="btn type-intra-white" onclick="handleRefuseFriend(this.dataset.username)" data-username=${data.content.username}>Refuse</button>
        </div>
    </div>`;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    toastContainer.innerHTML += toastHtml;
    
    const newToast = toastContainer.lastChild;
    const toastBootstrap = new bootstrap.Toast(newToast);
    toastBootstrap.show();
    
    newToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
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
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

export {notifSocket};
export {create_message_notif}
export {getClientId}
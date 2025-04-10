import { WebSocketManager } from "../../websockets/websockets.js";
import { navigateTo } from "../../spa/spa.js";

let client_id = null;
const clientId = await getClientId();
const notifSocket =  await WebSocketManager.initNotifSocket(clientId);

notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);
    
    if(message.data.action == "ACK_SEND_FRIEND_REQUEST") {
        let pending_group = document.querySelector('.pending_group');
        if(pending_group)
        {
            const parser = new DOMParser();
            const htmlString = 
            `<li class="list-group-item pending_item d-flex justify-content-between align-items-center" id="${message.data.content.username}">
                ${message.data.content.username}
                <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                    <button type="button" class="type-intra-green accept_friend" onclick="handleAcceptFriend(this.dataset.username)" data-username="${message.data.content.username}" id="${message.data.content.sender}">accept</button>
                    <button type="button" class="type-intra-white refuse_friend" onclick="handleRefuseFriend(this.dataset.username)" data-username="${message.data.content.username}">refuse</button>
                </div>
            </li>
            `
            const doc = parser.parseFromString(htmlString, "text/html");
            const pendingElement = doc.body.firstChild;
            pending_group.appendChild(pendingElement);
        }
        toasts(`New friend request from ${message.data.content.username}`);
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
                    <button type="button" class="type-intra-green delete_friend me-4" onclick="handleDeleteFriend(this.dataset.username)" data-username="${message.data.content.username}" >delete</button>
                </div>
            </li>
            `
            const doc = parser.parseFromString(add_to_friend, "text/html");
            const friendElement = doc.body.firstChild;
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
                    <button type="button" class="type-intra-green delete_friend me-4" onclick="handleDeleteFriend(this.dataset.username)" data-username="${message.data.content.username}" >delete</button>
                </div>
            </li>
            `
            const doc = parser.parseFromString(add_to_friend, "text/html");
            const friendElement = doc.body.firstChild;
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
        
        // const addFriendement = document.querySelector(".friends_group")
        // if(addFriendement)
        // {
        //     const parser = new DOMParser();
        //     const htmlAddElement = 
        //     `{% if show_friend_request %}
        //         <button type="button" class="type-intra-green friendrequest" onclick="handleAskFriend(new URLSearchParams(window.location.search).get('username'))">Friend Request</button>
        //     {%endif%}`
        //     const doc = parser.parseFromString(htmlAddElement, "text/html");
        //     const pendingFriendElement = doc.body.firstChild;
        //     addFriendement.appendChild(pendingFriendElement);
        // }
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
    const message = create_message_notif("accept_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleRefuseFriend = function(username) {
    const message = create_message_notif("refuse_friend_request", username);
    notifSocket.send(JSON.stringify(message));
};

window.handleDeleteFriend = function(username) {
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

function toasts(message){
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
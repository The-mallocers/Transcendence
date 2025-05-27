import { WebSocketManager } from "../../websockets/websockets.js"
import { navigateTo } from "../../spa/spa.js";
import { create_message_duel } from "../game/gamemode.js";
import { create_message_notif_block } from "../profile/profile.js";
import { toast_message } from "../profile/toast.js";
import { remove_toast } from "../profile/toast.js";
import { getClientId } from "../../utils/utils.js";
import { create_front_chat_room } from "../../utils/utils.js";

let client_id = null;
let room_id = null;
const notifSocket = WebSocketManager.notifSocket;

const clientId = await getClientId();
export const chatSocket = await WebSocketManager.initChatSocket(clientId);

const MAX_MESSAGE_LENGTH = 200;

function showActiveChat(show) {
    const noChat = document.getElementById('no-chat-selected');
    const activeChat = document.getElementById('active-chat');
    
    if (show) {
        noChat.classList.add('d-none');
        activeChat.classList.remove('d-none');
    } else {
        noChat.classList.remove('d-none');
        activeChat.classList.add('d-none');
    }
}

chatSocket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.data.action == "HISTORY_RECEIVED") {
        showActiveChat(true);
        displayHistory(message.data.content.messages);
        const messageId = document.getElementById("messageInput");
        if(messageId)
        {
            messageId.placeholder = `Send message to ${message.data.content.username}`
        }
    }
    else if(message.data.action == "NO_HISTORY")
        {
        showActiveChat(true);
        displayHistory([])
        const messageId = document.getElementById("messageInput");
        if(messageId)
        {
            messageId.placeholder = `Send message to ${message.data.error.username}`
        }
    }
    else if(message.data.action == "ALL_ROOM_RECEIVED") {
        displayRooms(message.data.content.rooms);
    }
    else if(message.data.action == "MESSAGE_RECEIVED") {
        if (message.data.content.room_id === room_id) {
            let chatHistory = document.querySelector('.chatHistory');
            
            const parser = new DOMParser();
            const htmlString = `<div class="msg ${clientId == message.data.content.sender ? "me align-self-end" : "you align-self-start"}">${message.data.content.message}</div>`;
            const doc = parser.parseFromString(htmlString, "text/html");
            const msgElement = doc.body.firstChild; // Get the actual <div> element
            
            chatHistory?.appendChild(msgElement);
            scrollToBottom(chatHistory);
            //Do things to show the new message on the front
        }
    }
    else if(message.data.action == "ERROR_MESSAGE_USER_BLOCK"){
        remove_toast();
        toast_message("You cant send message to block Friend")
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST") {
        create_front_chat_room(message.data.content.room,
                                message.data.content.username, 
                                message.data.content.sender, 
                                "Block",
                                message.data.content.profile_picture);
    }
    else if (message.data.action == "DUEL_CREATED") {
        navigateTo(`/pong/duel/?opponent=${message.data.content.opponent}`);
    }
    else if(message.data.action == "BLOCKED_USER"){ 
        remove_toast();
        toast_message("You have blocked this user");
        navigateTo('');
    }
}
                        
const messageInput = document.getElementById("messageInput")
if(messageInput){
    chatSocket?.addEventListener("open", (event) => {
            
        const message = {
            "event": "chat",
            "data": {
                "action": "get_all_room_by_client",
                "args": {}
            }
        };
        chatSocket.send(JSON.stringify(message));
    });
    messageInput?.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevents the default action (like form submission)
            let messageText = this.value.trim(); // Get the entered text and trim whitespace
            
            // Check message length
            if (messageText.length > MAX_MESSAGE_LENGTH) {
                toast_message(`Message too long. Maximum ${MAX_MESSAGE_LENGTH} characters allowed.`);
                return;
            }
            
            if (messageText.length === 0) {
                return; // Don't send empty messages
            }
            
            this.value = ""; // Clear the input field after handling
            
            // Sending this to the websocket
            const message = {
                "event": "chat",
                "data": {
                    "action": "send_message",
                    "args": {
                        "room_id": room_id,
                        "message": messageText
                    }
                }
            }

            chatSocket.send(JSON.stringify(message));
        }
    });

    const counterElement = document.createElement('div');
    counterElement.className = 'char-counter';
    counterElement.style.position = 'absolute';
    counterElement.style.right = '10px';
    counterElement.style.bottom = '40px';
    counterElement.style.fontSize = '0.8rem';
    counterElement.style.color = '#FFFFFF';
    
    messageInput.parentNode.insertBefore(counterElement, messageInput.nextSibling);
    
    messageInput?.addEventListener('input', function() {
        const remaining = MAX_MESSAGE_LENGTH - this.value.length;
        counterElement.textContent = `${remaining} characters remaining`;
        
        if (remaining < 20) {
            counterElement.style.color = '#dc3545';
        } else {
            counterElement.style.color = '#FFFFFF';
        }
    });
}

window.clickRoom = function (room) {
    room_id = room
    const message = {
        "event": "chat",
        "data": {
            "action": "get_history",
            "args": {
                "room_id": room,
            }
        }
    };
    if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify(message));
    }
}
window.handleChatProfile = function (username) {
    navigateTo(`/profile/?username=${username}`)
}

window.handleChatBlock = function (username) {
    const message = create_message_notif_block("block_unblock_friend", username, "block");
    notifSocket.send(JSON.stringify(message));
}

window.handleChatUnblock = function (username) {
    const message = create_message_notif_block("block_unblock_friend", username, "unblock");
    notifSocket.send(JSON.stringify(message));
}

window.handleChatDuel = function (usernameId) {

    const message = create_message_duel("create_duel", usernameId);
    notifSocket.send(JSON.stringify(message));
    // navigateTo('/pong/duel/');
}

async function displayHistory(message) {

    let chatHistory = document.querySelector('.chatHistory');
    chatHistory.innerHTML = "";
    for (let i = 0; i < message.length; i++) {
        const parser = new DOMParser();
        const htmlString = `<div class="msg ${clientId == message[i].sender ? "me align-self-end" : "you align-self-start"}">${message[i].message}</div>`;
        const doc = parser.parseFromString(htmlString, "text/html");
        const msgElement = doc.body.firstChild; // Get the actual <div> element

        chatHistory?.appendChild(msgElement);
    }
    scrollToBottom(chatHistory);
}

async function displayRooms(rooms) {
    let chatRooms = document.querySelector('.chatRooms');
    
    for (let i = 0; i < rooms.length; i++) {
        create_front_chat_room(rooms[i].room, 
                            rooms[i].player[0].username, 
                            rooms[i].player[0].id, 
                            rooms[i].player[0].status,
                            rooms[i].player[0].profile_picture)
    }
    scrollToBottom(chatRooms);
}

function scrollToBottom(element){
    element.scrollTop = element.scrollHeight;
}
import { WebSocketManager } from "../../websockets/websockets.js"
import { navigateTo } from "../../spa/spa.js";
import { create_message_duel } from "../game/gamemode.js";
import { create_message_notif_block } from "../profile/profile.js";
import { toast_message } from "../profile/toast.js";
import { remove_toast } from "../profile/toast.js";
import { getClientId } from "../../utils/utils.js";

let client_id = null;
let room_id = null;
const notifSocket = WebSocketManager.notifSocket;

const clientId = await getClientId();
export const chatSocket = await WebSocketManager.initChatSocket(clientId);


chatSocket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log(event.data);
    
    if (message.data.action == "HISTORY_RECEIVED") {
        displayHistory(message.data.content.messages);
    }
    else if(message.data.action == "NO_HISTORY")
        {
        displayHistory([])
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
            
            chatHistory.appendChild(msgElement);
            scrollToBottom(chatHistory);
            //Do things to show the new message on the front
        }
    }
    else if(message.data.action == "ERROR_MESSAGE_USER_BLOCK"){
        remove_toast();
        toast_message("You cant send message to block Friend")
    }
    else if(message.data.action == "NEW_FRIEND") {
        create_front_chat_room(message.data.content.room,
                                message.data.content.username, 
                                message.data.content.sender, 
                                "Block",
                                message.data.content.profile_picture);
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST") {
        create_front_chat_room(message.data.content.room,
                                message.data.content.username, 
                                message.data.content.sender, 
                                "Block",
                                message.data.content.profile_picture);
                            }
                        }
                        
const messageInput = document.getElementById("messageInput")
if(messageInput){
    chatSocket.addEventListener("open", (event) => {
        console.log("WebSocket is open now.");
            
        const message = {
            "event": "chat",
            "data": {
                "action": "get_all_room_by_client",
                "args": {}
            }
        };
        chatSocket.send(JSON.stringify(message));
    });
    messageInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevents the default action (like form submission)
            let message = this.value; // Get the entered text
            console.log("User entered:", message);
            this.value = ""; // Clear the input field after handling
            //Sending this to the websocket
            message = {
                "event": "chat",
                "data": {
                    "action": "send_message",
                    "args": {
                        "room_id": room_id,
                        "message": message
                    }
                }
            }
            console.log("room: " + room_id);
            chatSocket.send(JSON.stringify(message));
        }
    });
}

window.clickRoom = function(room){
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
    if(chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify(message));
    }
}
window.handleChatProfile = function(username)
{
    navigateTo(`/profile/?username=${username}`)
}

window.handleChatBlock = function(username)
{
    const message = create_message_notif_block("block_unblock_friend", username, "block");
    notifSocket.send(JSON.stringify(message));
}

window.handleChatUnblock = function(username)
{
    const message = create_message_notif_block("block_unblock_friend", username, "unblock");
    notifSocket.send(JSON.stringify(message));
}

window.handleChatDuel = function(usernameId)
{
    console.log(usernameId);
    const message = create_message_duel("create_duel",usernameId);
    notifSocket.send(JSON.stringify(message));
    navigateTo('/pong/duel/');
}

async function displayHistory(message) {
    console.log("Displaying history");
    let chatHistory = document.querySelector('.chatHistory');
    chatHistory.innerHTML = "";
    for (let i = 0; i < message.length; i++) {
        const parser = new DOMParser();
        const htmlString = `<div class="msg ${clientId == message[i].sender ? "me align-self-end" : "you align-self-start"}">${message[i].message}</div>`;
        const doc = parser.parseFromString(htmlString, "text/html");
        const msgElement = doc.body.firstChild; // Get the actual <div> element

        chatHistory.appendChild(msgElement);
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

function create_front_chat_room(room, username, usernameId, status, profilePicture = null){
    const newChat = document.querySelector('.chatRooms');
    if(newChat)
    {
        const imgSrc = profilePicture;

        const parser = new DOMParser();
        const htmlChat = 
        `<div class="roomroom container d-flex align-items-center justify-content-between">
            <button class="chat-${username} chat-button btn d-flex align-items-center gap-3">
                <img src="${imgSrc}" alt="${username}'s profile picture">
                <div>${username}</div>
            </button>
            
            <div class="dropdown">
                <button class="btn btn-secondary dropdown-toggle no-caret rounded-circle" type="button" id="dropdownMenu-${room}" data-bs-toggle="dropdown" aria-expanded="false">
                    ...
                </button>
                <ul class="dropdown-menu">
                    <li><button class="dropdown-item chat-profile" type="button">Profil</button></li>
                    <li><button class="dropdown-item chat-block" type="button">${status}</button></li>
                    <li><button class="dropdown-item chat-duel" type="button">Duel</button></li>
                </ul>
            </div>
        </div>`
        const doc = parser.parseFromString(htmlChat, "text/html");
        const chatElement = doc.body.firstChild;
        const chatButton = chatElement.querySelector(`.chat-${username}`)
        const chatProfile = chatElement.querySelector(`.chat-profile`);
        const chatBlock = chatElement.querySelector(`.chat-block`);
        const chatDuel = chatElement.querySelector(`.chat-duel`);

        chatButton.addEventListener('click', function() {
            console.log(room);
            const roomroomDiv = this.closest('.roomroom');
    
            roomroomDiv.classList.add('active-room');
            
            document.querySelectorAll('.roomroom.active-room').forEach(div => {
                if (div !== roomroomDiv) {
                    div.classList.remove('active-room');
                }
            });
            clickRoom(room)
        })
        chatProfile.addEventListener('click', function(){
            handleChatProfile(username);
        })
        chatBlock.addEventListener('click', function(){
            if(this.innerHTML == "Block"){
                this.innerHTML = "Unblock"
                handleChatBlock(username);
            }
            else{
                this.innerHTML = "Block"
                handleChatUnblock(username);
            }
            
        })
        chatDuel.addEventListener('click', function(){
            handleChatDuel(usernameId);
        })
        newChat.appendChild(chatElement);
    }
}

function scrollToBottom(element){
    element.scrollTop = element.scrollHeight;
}

export {create_front_chat_room}
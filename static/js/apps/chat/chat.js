import { WebSocketManager } from "../../websockets/websockets.js"
import { notifSocket } from "../profile/profile.js";
import { navigateTo } from "../../spa/spa.js";
import { create_message_duel } from "../game/gamemode.js";

let client_id = null;
let room_id = null;


function scrollToBottom(element){
    element.scrollTop = element.scrollHeight;
}

const clientId = await getClientId();
console.log("Got client ID :", clientId);
export const chatSocket = await WebSocketManager.initChatSocket(clientId);

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
    else if(message.data.action == "NEW_FRIEND") {
        create_front_chat_room(message);
    }
    else if (message.data.action == "MESSAGE_RECEIVED") {
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

document.getElementById("messageInput").addEventListener("keydown", function (event) {
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
        console.log("full data: " + JSON.stringify(message))
        chatSocket.send(JSON.stringify(message));
    }
});

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

}

window.handleChatDuel = function(usernameId)
{
    console.log(usernameId);
    const message = create_message_duel("create_duel",usernameId);
    notifSocket.send(JSON.stringify(message));
    navigateTo('/pong/duel/');
}

async function getClientId() {
    console.log("Getting client ID")
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
    console.log("Displaying rooms");
    console.log("the length: " + rooms.length)
    let chatRooms = document.querySelector('.chatRooms');
    chatRooms.innerHTML = "";
    let htmlString;
    
    for (let i = 0; i < rooms.length; i++) {
        const parser = new DOMParser();
        if(rooms[i].player.length > 1)
        {
            htmlString = 
            `<button class="roomroom container d-flex align-items-center gap-3">
                <img src="/static/assets/imgs/profile/default.png">
                <div>chat global</div>
            </button>`
        }
        else
        {
            let player = rooms[i].player[0];
            console.log(rooms[i]);
            if(player == undefined)
                player = "delete user";
            htmlString = 
            `<button class="roomroom chat-${player} container d-flex align-items-center gap-3">
                <img src="/static/assets/imgs/profile/default.png">
                <div>${player}</div>
            </button>`
        }
        const doc = parser.parseFromString(htmlString, "text/html");
        const roomElement = doc.body.firstChild;
        roomElement.addEventListener('click', ()=>{
            clickRoom(rooms[i].room)
        })

        chatRooms.appendChild(roomElement);
    }
    scrollToBottom(chatRooms);
}

function create_front_chat_room(message){
    const newChat = document.querySelector('.chatRooms');
    if(newChat)
    {
        const parser = new DOMParser();
        const htmlChat = 
        `<div class="roomroom container d-flex align-items-center justify-content-between">
            <button class="chat-${message.data.content.username} btn d-flex align-items-center gap-3">
                <img src="/static/assets/imgs/profile/default.png">
                <div>${message.data.content.username}</div>
            </button>
            
            <div class="dropdown">
                <button class="btn btn-secondary dropdown-toggle no-caret rounded-circle" type="button" id="dropdownMenu-${message.data.content.room}" data-bs-toggle="dropdown" aria-expanded="false">
                    ...
                </button>
                <ul class="dropdown-menu">
                    <li><button class="dropdown-item chat-profile" type="button">Profil</button></li>
                    <li><button class="dropdown-item chat-block" type="button">Block</button></li>
                    <li><button class="dropdown-item chat-duel" type="button">Duel</button></li>
                </ul>
            </div>
        </div>`
        const doc = parser.parseFromString(htmlChat, "text/html");
        const chatElement = doc.body.firstChild;
        const chatButton = chatElement.querySelector(`.chat-${message.data.content.username}`)
        const chatProfile = chatElement.querySelector(`.chat-profile`);
        const chatBlock = chatElement.querySelector(`.chat-block`);
        const chatDuel = chatElement.querySelector(`.chat-duel`);

        chatButton.addEventListener('click', function() {
            clickRoom(message.data.content.room)
        })
        chatProfile.addEventListener('click', function(){
            handleChatProfile(message.data.content.username);
        })
        chatBlock.addEventListener('click', function(){
            handleChatBlock(message.data.content.username);
        })
        chatDuel.addEventListener('click', function(){
            handleChatDuel(message.data.content.sender)
        })
        newChat.appendChild(chatElement);
    }
}
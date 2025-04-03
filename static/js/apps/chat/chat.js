// window.addEventListener('load', onPageLoad);
import { WebSocketManager } from "../../websockets/websockets.js"

let client_id = null;
let room_id = null; 


function scrollToBottom(element){
    element.scrollTop = element.scrollHeight;
}

const clientId = await getClientId();
console.log("Got client ID :", clientId);
const chatSocket = await WebSocketManager.initChatSocket(clientId);

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
    console.log("message send");

    if(message.data.action == "HISTORY_RECEIVED") {
        displayHistory(message.data.content.messages);
    }
    else if(message.data.action == "ALL_ROOM_RECEIVED") {
        displayRooms(message.data.content.rooms);
    }
    else if(message.data.action == "MESSAGE_RECEIVED") {
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

document.getElementById("messageInput").addEventListener("keydown", function(event) {
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
        chatSocket.send(JSON.stringify(message));
    }
});

// Attach event listener to a parent that exists before buttons are created
document.addEventListener("click", function(event) {
    if (event.target.classList.contains("roomroom")) { 
        console.log("chatSocket = ", chatSocket);
        const id = event.target.id;
        room_id = id;
        console.log("Clicked on room", id);
        
        const message = {
            "event": "chat",
            "data": {
                "action": "get_history",
                "args": {
                    "room_id": id,
                }
            }
        };
        //Dirty fucking hack because for some reason it tried to send the message twice.
        if(chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify(message));
        }
    }
});

async function getClientId() {
    // if (client_id !== null) return client_id;
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

async function displayHistory(message){
    console.log("Displaying history");
    let chatHistory = document.querySelector('.chatHistory');
    chatHistory.innerHTML = "";
    for (let i = 0; i < message.length; i++) {
        const parser = new DOMParser();
        const htmlString = `<div class="msg ${clientId == message[i].sender ? "me align-self-end" : "you align-self-start"}">${message[i].message}</div>`;
        const doc = parser.parseFromString(htmlString, "text/html");
        const msgElement = doc.body.firstChild; // Get the actual <div> element

        chatHistory.appendChild(msgElement);

        scrollToBottom(chatHistory);
    }
}

async function displayRooms(rooms){
    console.log("Displaying rooms");
    console.log("the length: " + rooms.length)
    let chatRooms = document.querySelector('.chatRooms');
    chatRooms.innerHTML = "";
    let htmlString;
    
    for (let i = 0; i < rooms.length; i++) {
        const parser = new DOMParser();
        if(rooms[i].player.length > 1)
        {
            htmlString = `<div id="${rooms[i].room}" class="roomroom container d-flex align-items-center gap-3">
            <img src="/static/assets/imgs/profile/default.png">
            <div>chat global</div>
        </div>`
        }
        else
        {
            let player = rooms[i].player[0];
            if(player == undefined)
                player = "delete user";
            htmlString = `<div id="${rooms[i].room}" class="roomroom container d-flex align-items-center gap-3">
                    <img src="/static/assets/imgs/profile/default.png">
                    <div>${player}</div>
                </div>`
        }
        const doc = parser.parseFromString(htmlString, "text/html");
        const roomElement = doc.body.firstChild;
        chatRooms.appendChild(roomElement);
    }
    scrollToBottom(chatRooms);
}
// window.addEventListener('load', onPageLoad);
import { WebSocketManager } from "../../websockets/websockets.js"

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
    console.log("Sending get_all_room_by_client message:", message);
    chatSocket.send(JSON.stringify(message));
});

chatSocket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log("Message received:", message);

    if (message.data.action == "HISTORY_RECEIVED") {
        displayHistory(message.data.content.messages);
    }
    else if(message.data.action == "NO_HISTORY")
    {
        displayHistory([])
    }
    else if(message.data.action == "ALL_ROOM_RECEIVED") {
        console.log("Rooms received:", message.data.content.rooms);
        if (message.data.content.rooms && Array.isArray(message.data.content.rooms)) {
            displayRooms(message.data.content.rooms);
        } else {
            console.error("Invalid rooms data format:", message.data.content.rooms);
            // Display error in UI or try to recover
        }
    } else if (message.data.action == "MESSAGE_RECEIVED") {
        // Only update the chat history if we're in the same room as the message
        if (message.data.content.room_id === room_id) {
            let chatHistory = document.querySelector('.chatHistory');

            const parser = new DOMParser();
            const htmlString = `<div class="msg ${clientId == message.data.content.sender ? "me align-self-end" : "you align-self-start"}">${message.data.content.message}</div>`;
            const doc = parser.parseFromString(htmlString, "text/html");
            const msgElement = doc.body.firstChild; // Get the actual <div> element

            chatHistory.appendChild(msgElement);
            scrollToBottom(chatHistory);
        } else {
            // Add visual indicator that there's a new message in another room
            const roomButton = document.getElementById(message.data.content.room_id);
            if (roomButton) {
                roomButton.classList.add('new-message');
            }
        }
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
        console.log("message_send: " + message.data);
        chatSocket.send(JSON.stringify(message));
    }
});

// Attach event listener to a parent that exists before buttons are created
document.addEventListener("click", function (event) {
    if (event.target.classList.contains("roomroom") || event.target.closest(".roomroom")) {
        // Get the actual button element (in case user clicked on child element)
        const roomButton = event.target.classList.contains("roomroom") ? 
                           event.target : 
                           event.target.closest(".roomroom");
        
        // Remove active class from all room buttons
        document.querySelectorAll(".roomroom").forEach(btn => {
            btn.classList.remove("active");
        });
        
        // Add active class to the clicked button
        roomButton.classList.add("active");
        
        // Remove 'new-message' class from the clicked button
        roomButton.classList.remove('new-message');
        
        const id = roomButton.id;
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
    console.log("Displaying rooms. Count:", rooms.length);
    let chatRooms = document.querySelector('.chatRooms');
    
    if (!chatRooms) {
        console.error("Could not find .chatRooms element");
        return;
    }
    
    let currentActiveRoomId = room_id; // Store the current active room ID
    chatRooms.innerHTML = "";
    
    if (rooms.length === 0) {
        console.log("No rooms to display");
        chatRooms.innerHTML = `<div class="no-rooms">No chat rooms available</div>`;
        return;
    }
    
    for (let i = 0; i < rooms.length; i++) {
        try {
            const room = rooms[i];
            console.log(`Processing room ${i}:`, room);
            
            if (!room || !room.room) {
                console.error(`Invalid room data at index ${i}:`, room);
                continue; // Skip this iteration
            }
            
            const parser = new DOMParser();
            const isActive = room.room === currentActiveRoomId ? " active" : "";
            let htmlString;
            
            if (room.player && room.player.length > 1) {
                htmlString = 
                `<button id="${room.room}" class="roomroom${isActive} container d-flex align-items-center gap-3">
                    <img src="/static/assets/imgs/profile/default.png">
                    <div>chat global</div>
                </button>`;
            } else {
                let player = room.player && room.player.length > 0 ? room.player[0] : "unknown";
                if (player == undefined)
                    player = "delete user";
                    
                htmlString = 
                `<button id="${room.room}" class="roomroom${isActive} chat-${player} container d-flex align-items-center gap-3">
                    <img src="/static/assets/imgs/profile/default.png">
                    <div>${player}</div>
                </button>`;
            }
            
            const doc = parser.parseFromString(htmlString, "text/html");
            const roomElement = doc.body.firstChild;
            chatRooms.appendChild(roomElement);
        } catch (error) {
            console.error(`Error processing room at index ${i}:`, error);
        }
    }
    
    // Don't scroll if no rooms were added
    if (rooms.length > 0) {
        scrollToBottom(chatRooms);
    }
}
// window.addEventListener('load', onPageLoad);
import { WebSocketManager } from "../../websockets/websockets.js"


const element  = document.querySelector("#clientID");
const clientId = element.dataset.clientId

// console.log(clientId)



let connectGeneralChat = (client_id) =>{
    
    WebSocketManager.initChatSocket(client_id);
    
    const chatSocket = WebSocketManager.chatSocket    
    chatSocket.onmessage = (event) => {
        console.log("message received")
        const message = JSON.parse(event.data);
    
        console.log(message);
    
    
        let chatHistory = document.querySelector('.chatHistory');
    
        const parser = new DOMParser();
        const htmlString = `<div class="msg ${clientId == message.senderId ? "me align-self-end" : "you align-self-start"}">${message.message}</div>`;
        const doc = parser.parseFromString(htmlString, "text/html");
        const msgElement = doc.body.firstChild; // Get the actual <div> element
    
        chatHistory.appendChild(msgElement);    
        //Do things to show the new message on the front
    }

    chatSocket.onclose = () => {
        console.log("chat.js here, socket closed");
    }
}

connectGeneralChat(clientId);






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
                    "room_id": "6da121108be243cc91c2f52ac4c9f611",
                    "message": "hello comment ca va ? from chat 1"
                }
            }
        }
        
        chatSocket.send(JSON.stringify(message));
    }
});

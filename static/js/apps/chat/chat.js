// window.addEventListener('load', onPageLoad);


let client_id = null;


const clientId = await getClientId();
// if (clientId == null) {
//     return ;
// }
console.log("Got client ID :", clientId);
const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/?id=' + clientId);

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



async function getClientId() {
    // if (client_id !== null) return client_id;
    console.log("Getting client ID")
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        console.log(data);

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

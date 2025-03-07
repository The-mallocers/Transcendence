window.addEventListener('load', onPageLoad);

export function onPageLoad() {
    console.log("page loaded !");
}

let client_id = null;


document.getElementById("messageInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevents the default action (like form submission)
      let message = this.value; // Get the entered text
      console.log("User entered:", message);
      this.value = ""; // Clear the input field after handling
    }
});

export async function connectToChat() {
    const clientId = await getClientId();
    if (clientId == null) {
        return ;
    }
    console.log("Got client ID :", clientId);
    const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/game/?id=' + clientId); //This will be game for now
}


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

window.connectToChat = connectToChat;
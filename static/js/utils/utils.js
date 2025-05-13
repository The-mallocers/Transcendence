export async function getClientId() {
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
            return null;
        }
        console.log("data:", data);
        if (data.client_id) {
            return data.client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}



export function sendWhenReady(socket, message) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(message);
    } else {
        socket.addEventListener('open', () => socket.send(message), { once: true });
    }
}
export const WebSocketManager = {
  gameSocket: null,
  chatSocket: null,
  notifSocket: null,
  
  async initGameSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId(); // Ensure client_id is available
    // }
    if (this.isSocketClosed(this.gameSocket)) {
      this.gameSocket = new WebSocket(`wss://${window.location.host}/ws/game/?id=${client_id}`);
      this.gameSocket.onopen = () =>
      {
        const message = {
          "event": "matchmaking",
          "data": {
              "action": "ping"
          }
        }
        console.log("Game socket connected");
        this.gameSocket.send(JSON.stringify(message))
      }
    }
    return this.gameSocket;
  },
  
  async initChatSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId();
    // }
    if (this.isSocketClosed(this.chatSocket)) {
      this.chatSocket = new WebSocket(`wss://${window.location.host}/ws/chat/?id=${client_id}`);
      this.chatSocket.onopen = () => {
        const message = {
          "event": "chat",
          "data": {
              "action": "ping"
          }
        }
        console.log("chat socket connected");
        this.chatSocket.send(JSON.stringify(message))
      }
    }
    return this.chatSocket;
  },

  async initNotifSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId();
    // }
    if (this.isSocketClosed(this.notifSocket)) {
      this.notifSocket = new WebSocket(`wss://${window.location.host}/ws/notification/?id=${client_id}`);
      this.notifSocket.onopen = () => {
        const message = {
          "event": "notification",
          "data": {
              "action": "ping"
          }
        }
        console.log("notif socket connected");
        this.notifSocket.send(JSON.stringify(message))
      }
    }
    return this.notifSocket;
  },

  closeAllSockets() {
    this.closeGameSocket();
    this.closeChatSocket();
    // this.closeNotifSocket();
  },
  
  closeGameSocket() {
    if (this.isSocketOpen(this.gameSocket)) {
      this.gameSocket.close();
      this.gameSocket = null;
      console.log("Game socket closed");
    }
  },
  
  closeChatSocket() {
    if (this.isSocketOpen(this.chatSocket)) {
      this.chatSocket.close();
      this.chatSocket = null;
      console.log("chat socket closed");
    }
  },
  closeNotifSocket() {
    console.log("Trying to close notif socket")
    console.log(this.isSocketOpen(this.notifSocket))
    if (this.isSocketOpen(this.notifSocket)) {
      this.notifSocket.close();
      this.notifSocket = null;
      console.log("notif socket closed");
    }
  },
  isSocketClosed(socket) {
    return (!socket || socket.readyState === WebSocket.CLOSED)
  },
  isSocketOpen(socket) {
    return (socket && socket.readyState === WebSocket.OPEN)
  }
};

console.log("in the websocket function");

// async function getClientId() {
//   if (client_id !== null) return client_id; // Avoid multiple calls

//   console.log("Getting client ID");
//   try {
//     const response = await fetch("/api/auth/getId/", {
//       method: "GET",
//       credentials: "include",
//     });
//     const data = await response.json();
//     console.log(data);

//     if (data.client_id) {
//       client_id = data.client_id; // Store globally
//       return client_id;
//     } else {
//       throw new Error(data.error);
//     }
//   } catch (error) {
//     console.error("Error retrieving client ID:", error);
//     return null;
//   }
// }

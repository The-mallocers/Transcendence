export const WebSocketManager = {
  gameSocket: null,
  chatSocket: null,
  notifSocket: null,
  
  async initGameSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId(); // Ensure client_id is available
    // }
    if (!this.gameSocket || this.gameSocket.readyState === WebSocket.CLOSED) {
      this.gameSocket = new WebSocket(`wss://${window.location.host}/ws/game/?id=${client_id}`);
      this.gameSocket.onopen = () => console.log("Game socket connected");
    }
    return this.gameSocket;
  },
  
  async initChatSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId();
    // }
    if (!this.chatSocket || this.chatSocket.readyState === WebSocket.CLOSED) {
      this.chatSocket = new WebSocket(`wss://${window.location.host}/ws/chat/?id=${client_id}`);
      this.chatSocket.onopen = () => console.log("chat socket connected");
    }
    return this.chatSocket;
  },
  async initNotifSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId();
    // }
    if (!this.notifSocket || this.notifSocket.readyState === WebSocket.CLOSED) {
      this.notifSocket = new WebSocket(`wss://${window.location.host}/ws/notification/?id=${client_id}`);
      this.notifSocket.onopen = () => console.log("notif socket connected");
    }
    return this.notifSocket;
  },

  closeAllSockets() {
    this.closeGameSocket();
    this.closeChatSocket();
    // this.closeNotifSocket();
  },
  
  closeGameSocket() {
    if (this.gameSocket && this.gameSocket.readyState === WebSocket.OPEN) {
      this.gameSocket.close();
      this.gameSocket = null;
      console.log("Game socket closed");
    }
  },
  
  closeChatSocket() {
    if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
      this.chatSocket.close();
      this.chatSocket = null;
      console.log("chat socket closed");
    }
  },
  closeNotifSocket() {
    if (this.notifSocket && this.notifSocket.readyState === WebSocket.OPEN) {
      this.notifSocket.close();
      this.notifSocket = null;
      console.log("notif socket closed");
    }
  }
};

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

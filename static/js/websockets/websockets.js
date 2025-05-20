import { setUpTournamentSocket } from "../tournaments/tournamentsSocketHandlers.js";

export const WebSocketManager = {
  gameSocket: null,
  chatSocket: null,
  notifSocket: null,
  tournamentSocket: null,

  async initGameSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId(); // Ensure client_id is available
    // }
      if (this.isSocketClosed(this.gameSocket)) {
      this.gameSocket = new WebSocket(`wss://${window.location.host}/ws/game/?id=${client_id}`);
          this.gameSocket.onopen = () => {
              const message = {
                  "event": "matchmaking",
                  "data": {
                      "action": "ping"
                  }
              }
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
              this.notifSocket.send(JSON.stringify(message));
          }
    }
    return this.notifSocket;
  },

  async initTournamentSocket(client_id) {
    // if (!client_id) {
    //   client_id = await getClientId();
    // }
      if (this.isSocketClosed(this.tournamentSocket)) {
      this.tournamentSocket = new WebSocket(`wss://${window.location.host}/ws/tournament/?id=${client_id}`);
          this.tournamentSocket.onopen = () => {
              const message = {
                  "event": "tournament",
                  "data": {
                      "action": "ping"
                  }
              }
              this.tournamentSocket.send(JSON.stringify(message));
              setUpTournamentSocket(this.tournamentSocket);
          }

        }
    return this.tournamentSocket;
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
              this.notifSocket.send(JSON.stringify(message))
          }
    }
    return this.notifSocket;
  },

  closeAllSockets() {
    this.closeGameSocket();
    this.closeChatSocket();
    // this.closeNotifSocket();
    // this.closeTournamentSocket();
  },

  closeGameSocket() {
      if (this.isSocketOpen(this.gameSocket)) {
      this.gameSocket.close();
      this.gameSocket = null;
    }
  },

  closeTournamentSocket() {
    if (this.isSocketOpen(this.tournamentSocket)) {
    this.tournamentSocket.close();
    this.tournamentSocket = null;
  }
},

  closeChatSocket() {
      if (this.isSocketOpen(this.chatSocket)) {
      this.chatSocket.close();
      this.chatSocket = null;
    }
  },
  closeNotifSocket() {
      if (this.isSocketOpen(this.notifSocket)) {
      this.notifSocket.close();
      this.notifSocket = null;
    }
  },
    isSocketClosed(socket) {
        return (!socket || socket.readyState === WebSocket.CLOSED)
    },
    isSocketOpen(socket) {
        return (socket && socket.readyState === WebSocket.OPEN)
  }
};


// async function getClientId() {
//   if (client_id !== null) return client_id; // Avoid multiple calls

//   try {
//     const response = await fetch("/api/auth/getId/", {
//       method: "GET",
//       credentials: "include",
//     });
//     const data = await response.json();

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

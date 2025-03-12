// websocket-manager.js
export const WebSocketManager = {
  gameSocket: null,
  chatSocket: null,
  
  // Initialize a specific socket
  initGameSocket() {
    if (this.gameSocket === null || this.gameSocket.readyState === WebSocket.CLOSED) {
      this.gameSocket = new WebSocket('ws://' + window.location.host + '/ws/game/?id=' + client_id);
      this.gameSocket.onopen = () => console.log('Game socket connected');
    }
    return this.gameSocket;
  },
  
  initchatSocket() {
    if (this.chatSocket === null || this.chatSocket.readyState === WebSocket.CLOSED) {
      this.chatSocket = new WebSocket('ws://' + window.location.host + '/ws/notifications/?id=' + client_id);
      this.chatSocket.onopen = () => console.log('Notification socket connected');
    }
    return this.chatSocket;
  },
  
  // Close all sockets
  closeAllSockets() {
    this.closeGameSocket();
    this.closeChatSocket();
  },
  
  // Close specific sockets
  closeGameSocket() {
    if (this.gameSocket && this.gameSocket.readyState === WebSocket.OPEN) {
      this.gameSocket.close();
      this.gameSocket = null;
      console.log('Game socket closed');
    }
  },
  
  closeChatSocket() {
    if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
      this.chatSocket.close();
      this.chatSocket = null;
      console.log('Notification socket closed');
    }
  }
};
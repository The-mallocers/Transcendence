// websocket-manager.js
export const WebSocketManager = {
  gameSocket: null,
  chatSocket: null,
  
  // Initialize a specific socket
  initGameSocket() {
    if (this.gameSocket === null || this.gameSocket.readyState === WebSocket.CLOSED) {
      this.gameSocket = new WebSocket('ws://' + window.location.host + '/ws/game/?id=' + client_id);
      // this.gameSocket.onopen = () => console.log('Game socket connected');
    }
    return this.gameSocket;
  },
  
  initchatSocket() {
    if (this.chatSocket === null || this.chatSocket.readyState === WebSocket.CLOSED) {
      this.chatSocket = new WebSocket('ws://' + window.location.host + '/ws/notifications/?id=' + client_id);
      this.chatSocket.onopen = () => console.log('chat socket connected');
    }
    return this.chatSocket;
  },
  
  closeAllSockets() {
    this.closeSocket(this.gameSocket, 'game');
    this.closeSocket(this.chatSocket, 'chat');
  },
  
  // Generic function to close a specific socket
  closeSocket(socket, socketName) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close();
      this[`${socketName}Socket`] = null;
      console.log(`${socketName} socket closed`);
    }
  }
};
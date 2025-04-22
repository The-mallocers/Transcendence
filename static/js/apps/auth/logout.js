import { navigateTo } from '../../spa/spa.js';
import { WebSocketManager } from "../../websockets/websockets.js"



function logout() {
    console.log("logout.js online")
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    WebSocketManager.closeNotifSocket();
    fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})  // sending an empty body for some reasons
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Logout successful:', data);
            navigateTo('/auth/login')
        })
        .catch(error => {
            console.error('Error during logout:', error);
        });
}

let element = document.querySelector("#logout-btn");


element.addEventListener("click", (e) => {
    logout(e);
})



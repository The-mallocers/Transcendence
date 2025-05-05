import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from "../../websockets/websockets.js"


async function logout() {
    console.log("logout.js online");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    WebSocketManager.closeNotifSocket();

    try {
        const response = await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})  // sending an empty body for some reasons
        });

        const data = await response.json();
        if (response.status == 302) {
            console.log(data)
            navigateTo(data.redirect)
        }
        else if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        else{
            console.log('Logout successful:', data);
            navigateTo('/auth/login');
        }
    } catch (error) {
        console.error('Error during logout:', error);
    }
}

const element = document.querySelector("#logout-btn");


element?.addEventListener("click", (e) => {
    logout(e);
})



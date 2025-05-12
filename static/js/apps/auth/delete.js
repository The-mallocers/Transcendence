import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from "../../websockets/websockets.js"


async function delete_account() {
    console.log("delete_account.js online");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    WebSocketManager.closeNotifSocket();

    try {
        const response = await fetch('/api/auth/delete_account/', {
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
        } else if (!response.ok) {
            throw new Error('Network response was not ok');
        } else {
            console.log('Delete successful:', data);
            navigateTo('/auth/login');
        }
    } catch (error) {
        console.error('Error during delete_account:', error);
    }
}

const element = document.querySelector("#delete-btn");

element?.addEventListener("click", (e) => {
    delete_account(e);
})



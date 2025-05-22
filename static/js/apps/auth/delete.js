import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from "../../websockets/websockets.js"
import {remove_toast} from "../profile/toast.js";
import {toast_message} from "../profile/toast.js";


async function delete_account() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    WebSocketManager.closeNotifSocket();
    WebSocketManager.closeTournamentSocket();

    try {
        const response = await fetch('/api/auth/delete_account/', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})  // sending an empty body for some reasons
        });

        const data = await response.json();
        if (response.status == 302) {
            navigateTo(data.redirect)
        }
        else if (response.status == 401){
            remove_toast();
            toast_message(data.error);
        }else if (!response.ok) {
            throw new Error('Network response was not ok');
        } else {
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

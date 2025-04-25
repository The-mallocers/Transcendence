import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from "../../websockets/websockets.js"


const data = {
    profile: {
        username: username,
        email: email
    },
    password: {
        password: password,
        passwordcheck: passwordcheck
    }
}


async function update() {

    console.log("update_infos.js online");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    try {
        const response = await fetch('/api/auth/update/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)  // sending an empty body for some reasons
        });

        const data = await response.json();
        if (response.ok) {
            showFeedback("Profile picture uploaded successfully!");
        } else {
            showFeedback(data?.profile_picture?.[0] || "Something went wrong.", false);
        }
    } catch (error) {
        const errorMessage = "Something went wrong, please upload a valid image 1000x1000 at most";
        showFeedback(errorMessage, false);
    }
}

const element = document.querySelector("#update-btn");

element.addEventListener("click", (e) => {
    update();
})



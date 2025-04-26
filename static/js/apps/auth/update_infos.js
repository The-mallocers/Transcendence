import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from "../../websockets/websockets.js"


async function update() {

    const form = document.querySelector("form");
    const error = document.getElementById("error-message");
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordcheck = document.getElementById('password_check').value;

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    try {
        const dataForm = {
            profile: {
                username: username,
                email: email
            },
            password: {
                password: password,
                passwordcheck: passwordcheck
            }
        }
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataForm)
        });

        const data = await response.json();
        console.log(data)
        if (response.ok) {
            console.log("We changed the stuff like you wanted !");
        } else {
            error.textContent = "Error updating";
            console.log("Some errors happened while changing stuff");
        }
    } catch (error) {
        console.log("Error with the fetch operation");
    }
}

const element = document.querySelector("#update-btn");

element.addEventListener("click", (e) => {
    update();
})



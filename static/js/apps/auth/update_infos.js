import {handleErrorFront, isPasswordcheckValid} from './register.js';

async function update() {
    const form = document.querySelector("form");
    const error = document.getElementById("error-message");
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordcheck = document.getElementById('password_check').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (!isPasswordcheckValid(password, passwordcheck)) {
        return;
    }

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
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataForm)
        });

        const data = await response.json();
        if (response.ok) {
            error.textContent = "Informations updated succesfully";
            updateFrontInformation();
            error.style.color = "green";
        } else {
            error.textContent = "Error updating";
            error.style.color = "red";
            handleErrorFront(data);
        }
    } catch (e) {
        error.textContent = "Error updating";
        error.style.color = "red";
    }
}

const element = document.querySelector("#update-btn");

element.addEventListener("click", (e) => {
    update();
})

function updateFrontInformation() {
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;

    if (username) {
        document.getElementById('currusername').value = `${username}`;
    }
    if (email) {
        document.getElementById('curremail').value = `${email}`;
    }
}

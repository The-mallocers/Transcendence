import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from '../../websockets/websockets.js';
import {getClientId} from '../../utils/utils.js';

function register(event) {
    console.log("I am register.js")
    event.preventDefault();
    const form = document.querySelector("form");
    const error = document.getElementById("error-message");

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordcheck = document.getElementById('password_check').value;

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
    if (!isPasswordcheckValid(password, passwordcheck)) {return ;}
    
    fetch(form.action, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/json"
        },
    })
        .then(response => {
            if (response.ok) {
                navigateTo('/');
            } else {
                console.log("we registered badly")
                console.log(response);
                response.json().then(errorData => {
                    console.log(errorData);
                    error.textContent = "Error registering";
                    handleErrorFront(errorData);
                });
            }
        })
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
        });
}

let element = document.querySelector("#register-btn");

element?.addEventListener("click", (e) => {
    register(e)
})

//This is a frontend check to avoid needing to ask the backend for validation, even if we still do.
export function isPasswordcheckValid(password, passwordcheck) {
    if (password === passwordcheck) {
        return true
    }
    else {
        clearAllErrorMessages();
        displayErrorMessage('password', "Passwords do not match.");
        displayErrorMessage('password_check', "Passwords do not match.");
        return false
    }
}

export function handleErrorFront(errorData) {
    clearAllErrorMessages();
    
    if ("profile" in errorData) {
        if ("username" in errorData['profile']) {
            displayErrorMessage('username', errorData['profile']['username']);
        }
        if ("email" in errorData['profile']) {
            displayErrorMessage('email', errorData['profile']['email']);
        }
    }
    console.log("Hello, error data is:", errorData);
    if ("password" in errorData) {
        if ("password" in errorData['password']) {
                displayErrorMessage('password', errorData['password']['password']);
        }
        if ("passwordcheck" in errorData['password']) {
            displayErrorMessage('password_check', errorData['password']['passwordcheck']);
        }
        if ("non_field_errors" in errorData["password"] ) {
            console.log("Here we go")
            displayErrorMessage('password', errorData["password"]["non_field_errors"]);
            displayErrorMessage('password_check', errorData["password"]["non_field_errors"]);
        }
    }
}


export function displayErrorMessage(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    errorElement.style.color = 'red';
    errorElement.style.fontSize = '0.8rem';
    errorElement.style.marginTop = '4px';
    
    field.parentNode.insertBefore(errorElement, field.nextSibling);
    
    field.addEventListener('focus', function() {
        const errorMsg = this.parentNode.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }, { once: true });
}

function clearAllErrorMessages() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
}


//Little trick to deal with annoying edge case of logout per invalid jwt token not closing ws
async function socketCheck() {
    if (await getClientId() == null && WebSocketManager.isSocketOpen(WebSocketManager.notifSocket)) {
        console.log("Allo");
        WebSocketManager.closeNotifSocket();
    }
}

await socketCheck();
import { navigateTo } from '../../spa/spa.js';

console.log("I am register.js")

const form = document.querySelector("form");
const error = document.getElementById("error-message");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const data = {
        profile: {
            username: username,
            email: email
        },
        password: {
            password: password
        }
    }

    fetch(form.action, {
        method: "POST",
        body: data,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
            window.location.href = '/';
            } else {
                error.textContent = data.message
        }
        })
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
        });
});

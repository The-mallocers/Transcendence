import { navigateTo } from '../../spa/spa.js';

export function register (event) {
    console.log("I am register.js")
    event.preventDefault();
    const form = document.querySelector("form");
    const error = document.getElementById("error-message");

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
        },
        player : {
            nickname: username
        }
    }
    console.log(data);
    console.log()

    fetch(form.action, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/json"
        },
    })
        .then(response => {
            if (response.ok)
            {
                navigateTo('/');
            }
            else {
                console.log("we registered badly")
                console.log(response);
                response.json().then(data => {
                    console.log("Error data:", data);
                    error.textContent = data[0];
                });
            }
        })
        // .then(data => {
        //     if (data.ok) {
        //         console.log("we registered succesfully")
        //         // window.location.href = '/';
        //         navigateTo("/");
        //     } else {
        //         console.log("we registered badly")
        //         console.log(data);
        //         error.textContent = "You typed either a shit email OR a shit password (shit usernames are allowed"
        // }
        // })
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
        });
};

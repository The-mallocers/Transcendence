import {navigateTo} from '../../spa/spa.js';

console.log("Login has been loaded")

function login(e) {

    e.preventDefault();


    const form = document.querySelector("form");
    const formData = new FormData(form);
    const errorDiv = document.getElementById("error-message")

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
        .then(async response => {
            if (response.ok) {
                console.log("trying to navigate to index");
                navigateTo('/');
            } else if (response.status === 302) {
                const data = await response.json();
                navigateTo(data.redirect); //2FA
            } else {
                console.log("Fetch of login failed");
                response.json().then(errorData => {
                    errorDiv.textContent = errorData.error || "An error occurred";
                });
            }
        })
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
            errorDiv.textContent = "Error, please check your internet and try again later";
        });


}

let element = document.querySelector("#login-btn");

element.addEventListener("click", (e) => {
    login(e)
})
//Add logic to redirect to 2fa screen if needed


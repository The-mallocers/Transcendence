import { navigateTo } from '../../spa/spa.js';
import { reloadScriptsSPA } from '../../spa/spa.js';

console.log("Login has been loaded")



document.addEventListener('SpaLoaded',  (e) => {
    console.log("checking out e");
    console.log(e);
    let events = e.detail.events
    events.forEach(element => {
        document.getElementById(element.id).addEventListener(element.event_type, element.func)
    });
    reloadScriptsSPA();
    console.log("My own page loaded ! my own event !");
});


if (document.documentgetElementById("testevent"))
{
    document.getElementById("testevent").addEventListener('click',  (e) => {
        console.log("login click !");
    });
}



export function login(e) {
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
        .then(response => {
            if (response.ok) {
                console.log("trying to navigate to index");
                navigateTo('/');
            }
            else if (response.status === 302) {
                response.json().then(data => {
                    console.log("trying to navigate to 2FA");
                    console.log("redirect is :", data.redirect)
                    navigateTo(data.redirect); //2FA
                })
            }
            else {
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
};

//Add logic to redirect to 2fa screen if needed


import { navigateTo } from '../../spa/spa.js';
import { reloadScriptsSPA } from '../../spa/spa.js';

console.log("Login has been loaded")



document.addEventListener('SpaLoaded',  (e) => {
    // console.log("checking out e");
    // console.log(e);
    // let events = e.detail.events

    // if(events){
    //     events.forEach(element => {
    //         const elementToListen = document.getElementById(element.id)
    //         if (elementToListen)
    //             elementToListen.addEventListener(element.event_type, element.func)
    //     });
    // }

    // e.detail.funct();
    // reloadScriptsSPA()
});






function login() {
    let laDivTest = document.querySelector("#testdiv")
    console.log(laDivTest)
    if (laDivTest)
        document.querySelector("#testdiv").addEventListener('click', ()=>console.log("Oh"))



    let e = document.querySelector("#login-btn");

    // console.log("lalalalalalalalal", e)
    if (e){
        e.addEventListener("click", function(event) {
            event.preventDefault();  // Correct way to call preventDefault on event
            // Your logic here

    
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
        });
    }
   
};




login()


//Add logic to redirect to 2fa screen if needed


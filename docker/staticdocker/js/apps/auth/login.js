import { navigateTo } from '../../spa/spa.js';


const AUTH_CONFIG = {
    clientId: 'u-s4t2ud-fba0f059cba0019f374c8bf89cb3a81ead9ef0cb218380d9344c21d99d1f9b3e',
    redirectUri: 'https://localhost:8000/auth/auth42',
    authorizationEndpoint: 'https://api.intra.42.fr/oauth/authorize',
    tokenEndpoint: 'https://api.intra.42.fr/oauth/token',
    userInfoEndpoint: 'https://api.intra.42.fr/v2/me'
};

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
        }
        else if (response.status === 302) {
            const data = await response.json();
            navigateTo(data.redirect); //2FA
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

let element = document.querySelector("#login-btn");

element.addEventListener("click", (e)=>{login(e)} )

//Add logic to redirect to 2fa screen if needed
const login42Button = document.getElementById('auth42');
if (login42Button) {
    login42Button.addEventListener('click', () => {
        const params = new URLSearchParams({
            client_id: AUTH_CONFIG.clientId,
            redirect_uri: AUTH_CONFIG.redirectUri,
            response_type: 'code',
            scope: 'public'
        });

        window.location.href = `${AUTH_CONFIG.authorizationEndpoint}?${params}`;
    });
}
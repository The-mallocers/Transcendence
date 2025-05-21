import {navigateTo} from '../../spa/spa.js';
import {WebSocketManager} from '../../websockets/websockets.js';
import {getClientId} from '../../utils/utils.js';

const AUTH_CONFIG = {
    clientId: 'u-s4t2ud-fba0f059cba0019f374c8bf89cb3a81ead9ef0cb218380d9344c21d99d1f9b3e',
    redirectUri: `https://${window.location.hostname}:8000/auth/auth42`,
    authorizationEndpoint: 'https://api.intra.42.fr/oauth/authorize',
    tokenEndpoint: 'https://api.intra.42.fr/oauth/token',
    userInfoEndpoint: 'https://api.intra.42.fr/v2/me'
};


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
                navigateTo('/');
            } else if (response.status === 302) {
                const data = await response.json();
                navigateTo(data.redirect); //2FA
            } else {
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

element.addEventListener("click", (e)=>{login(e)} )
let popRef = null
let meow = document.querySelector("#cancel")


const login42Button = document.getElementById('auth42');
if (login42Button) {
    login42Button.addEventListener('click', () => {
        const params = new URLSearchParams({
            client_id: AUTH_CONFIG.clientId,
            redirect_uri: AUTH_CONFIG.redirectUri,
            response_type: 'code',
            scope: 'public'
        });

        window.location.href = `${AUTH_CONFIG.authorizationEndpoint}?${params}`


        /// leaving this in comments in case i think i should go back later (i hope i wont tho)
        // // Open the login page in a new tab
        // const authWindow = window.open(
        //     `${AUTH_CONFIG.authorizationEndpoint}?${params}`,
        //     '42Auth',
        //     'width=600,height=700'
        // );

        // const popRef = window.open(
        //     `${AUTH_CONFIG.authorizationEndpoint}?${params}`,
        // );
        // );`;


        // let meowInterval = setInterval(async ()=>{
        //     const response = await fetch("/api/auth/getId/", {
        //         method: "GET",
        //         credentials: "include",
        //     });

        //     if (response.status == 200){
        //         clearInterval(meowInterval)
        //         navigateTo("/")
        //     }

        //     // if (document.cookie !== previousCookies) {
        //     //     // previousCookies = document.cookie;
        //     //     // // Do something with the new cookies


        //     // }
        // },3000)

        // setTimeout(() => {
        //     popRef.close()
        //     clearInterval(meowInterval)
        //     // throw timeout error toast to notify user they should close the tab and 
        // }, 10000);

        // setTimeout(()=>{
        //     navigateTo("/")
        // }, 2000)

    });
}

//Little trick to deal with annoying edge case of logout per invalid jwt token not closing ws
async function socketCheck() {
    if (await getClientId() == null && WebSocketManager.isSocketOpen(WebSocketManager.notifSocket)) {
        WebSocketManager.closeNotifSocket();
    }
}

await socketCheck();

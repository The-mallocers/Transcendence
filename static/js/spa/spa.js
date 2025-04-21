import { WebSocketManager } from "../websockets/websockets.js"
import { isGameOver } from "../apps/game/VarGame.js"
import * as html from "../utils/html_forms.js"
import { routes } from "../utils/routes.js";
// let notifSocket = null;
// let clientId = null;

class Router {
    constructor(routes) {
        this.routes = routes;
        this.rootElement = document.getElementById('app');
        this.init();
    }

    init() {
        window.addEventListener('popstate', () => this.handleLocation());
    }

    async handleLocation() {

        // clientId = await getClientId();
        // notifSocket = await WebSocketManager.initNotifSocket(clientId);
        const path = window.location.pathname;

        // console.log(window.location.search);
        // console.log("looking for the path: ", path)
        const route = this.routes.find(r => r.path === path);

        if (!route) {
            navigateTo("/error/404/");
        } else {
            try {
                // console.log("About to try the route template of the route :", route);
                const content = await route.template(window.location.search ? window.location.search : "");
                this.rootElement.innerHTML = content;
                this.reloadScripts();
            } catch (error) {
                console.error('Route rendering failed:', error);
            }
        }
    }

    reloadScripts() {
        const scripts = this.rootElement.querySelectorAll('script');
        console.log("scripts = ", scripts)
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy src or inline content
            if (oldScript.src) {
                newScript.src = oldScript.src + "?t=" + new Date().getTime();
            } else {
                newScript.textContent = oldScript.textContent;
            }

            Array.from(oldScript.attributes).forEach(attr => {
                if (attr.name !== 'src') { // Skip src as we handled it above
                    newScript.setAttribute(attr.name, attr.value);
                }
            });

            console.log(oldScript)
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }

    navigate(path) {

        let splitedPath = path.split("/")
        console.log(splitedPath)
        if (splitedPath.includes("pong")) {
            WebSocketManager.closeChatSocket()
        } else {
            WebSocketManager.closeAllSockets(); //for now we close all
        }
        if (window.location.pathname == path) {
            return;
        }

        isGameOver.gameIsOver = true;
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

window.onload = async () => {
    await router.handleLocation();
}


// Navigation helper
export function reloadScriptsSPA() {
    router.reloadScripts();
}

export function navigateTo(path) {
    router.navigate(path);
}


// Example route definitions
const header = {
    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    'X-Requested-With': 'XMLHttpRequest',
};

export async function fetchRoute(path) {
    console.log("fetching the path :", path)
    try {
        const response = await fetch(path, {
            headers: header,
            credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
            return data.html;
        } else if (response.status === 302) {
            console.log(data, response)
            return navigateTo(data.redirect)
        } else if (response.status === 401) {
            return navigateTo(data.redirect)
        } else if (response.status >= 400 && response.status < 500) {
            return data.html;
        } else if (response.status == 500) {
            return html.Internal_Server_Error;
        }
    } catch (error) {
        console.error(error.message);
        return html.Fetch_Error;
    }
}

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    const routeElement = e.target.closest('[data-route]');
    if (routeElement) {
        const route = routeElement.dataset.route;
        // console.log("in data route :", route);
        navigateTo(route);
    }
});



document.addEventListener("keypress", function (event) {
    const routeElement = event.target.closest('.searchBar');
    if (event.key === "Enter") {
        if (routeElement) {
            event.preventDefault();
            const inputElement = routeElement.querySelector('input');
            let query = inputElement.value;
            navigateTo('/profile/?username=' + query)
            inputElement.value = '';
        }
    }
})

const router = new Router(routes);

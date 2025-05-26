import {WebSocketManager} from "../websockets/websockets.js"
import {isGameOver, localState} from "../apps/game/VarGame.js"
import * as html from "../utils/html_forms.js"
import {routes} from "../utils/routes.js";
import {getClientId} from "../utils/utils.js";
import { toast_message } from "../apps/profile/toast.js";
import { remove_toast } from "../apps/profile/toast.js";

window.intervalsManager = []
class Router {
    constructor(routes) {
        this.routes = routes;
        this.rootElement = document.getElementById('app');
        this.init();
    }

    init() {
        window?.addEventListener('popstate', () => this.handleLocation());
    }

    async handleLocation() {
        console.log("handle location !");
        console.log(window.location.pathname);
        for (let id of window.intervalsManager) {
            clearInterval(id);
        }
        window.intervalsManager.length = 0;
        //Now making the notif ws in navigation
        navigationChecks();
        if (WebSocketManager.isSocketClosed(WebSocketManager.notifSocket)) {
            const clientId = await getClientId();
            if (clientId) {
                await WebSocketManager.initNotifSocket(clientId);
            }
        }
        if (WebSocketManager.isSocketClosed(WebSocketManager.tournamentSocket)) {
            const clientId = await getClientId();
            if (clientId) {
                await WebSocketManager.initTournamentSocket(clientId);
            }
        }
        const path = window.location.pathname;
        const route = this.routes.find(r => r.path === path);

        if (!route) {
            navigateTo("/error/404/");
        } else {
            try {
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

            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }

    navigate(path) {
        if (window.location.pathname == path) {
            return;
        }
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

function navigationChecks() {
    const path = window.location.pathname;
    let splitedPath = path.split("/")
    if (path != '/pong/arena/') {
        localState.gameIsLocal = false;
    };
    if (splitedPath.includes("pong")) {
        if (splitedPath.includes("duel") || splitedPath.includes("arena") || splitedPath.includes("matchmaking")) {
            console.log("Closing chat sockets");
            WebSocketManager.closeChatSocket();
        } else {
            console.log("Closing all sockets");
            WebSocketManager.closeAllSockets();
        }
    } else {
        WebSocketManager.closeAllSockets(); //for now we close all
    }
    isGameOver.gameIsOver = true;
}


window.onload = async () => {
    await router.handleLocation();
}


// Navigation helper
export function reloadScriptsSPA() {
    router.reloadScripts();
}

export function navigateTo(path) {
    //////////
    //////////
    router.navigate(path);
}


// Example route definitions
const header = {
    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    'X-Requested-With': 'XMLHttpRequest',
};

export async function fetchRoute(path) {
    try {
        const response = await fetch(path, {
            headers: header,
            credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
            return data.html;
        } else if (response.status === 302) {
            //Add toast
            if (window.location.pathname != "/") {
                remove_toast();
                if (data.message) {
                    toast_message(data.message);
                }
                else {
                    toast_message("Redirecting");
                }
            }
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
document?.addEventListener('click', async (e) => {
    const routeElement = e.target.closest('[data-route]');
    if (routeElement) {
        const route = routeElement.dataset.route;
        navigateTo(route);
    }
});



document?.addEventListener("keypress", function (event) {
    const routeElement = event.target.closest('.searchBar');
    if (event.key === "Enter") {
        if (routeElement) {
            event.preventDefault();
            const inputElement = routeElement.querySelector('input');
            let query = inputElement.value;
            query = query.substring(0, 50);
            navigateTo('/profile/?username=' + query)
            inputElement.value = '';
        }
    }
})

const router = new Router(routes);

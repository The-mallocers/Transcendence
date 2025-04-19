import {WebSocketManager} from "../websockets/websockets.js"
import {isGameOver} from "../apps/game/VarGame.js"
import * as html from "../utils/html_forms.js"
// let notifSocket = null;
// let clientId = null;
class Router {
    constructor(routes) {
        this.routes = routes;
        this.rootElement = document.getElementById('app');
        this.init();
    }

    //Claude said the above method is better than : document.querySelector('#app');
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
            console.log("test ?? aaaaaaaaa")
        } else {
            WebSocketManager.closeAllSockets(); //for now we close all
            console.log("test ?? bbbbbbbbb")
        }
        if (window.location.pathname == path) {
            console.log("test ?? ccccccccc")
            return;
        }

        isGameOver.gameIsOver = true;
        //In the future, we will have to do some better logics with the path to decide if we want to close
        //a websocket or not.

        window.history.pushState({}, '', path);
        console.log("test ??", path)
        this.handleLocation();
    }
}

window.onload = async () => {
    console.log(pongRoute.possibleRoutes)
    // console.log(window.location.pathname

    //Add the creation of the websocket here
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

async function fetchRoute(path) {
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
           return 
        }
    } catch (error) {
        console.error(error.message);
        return html.Fetch_Error;
    }
}

const routes = [
    {
        path: '/',
        template: async () => {
            return await fetchRoute('/pages/');
        },
    },
    {
        path: '/auth/login',
        template: async () => {
            return await fetchRoute('/pages/auth/login');
        },
    },
    {
        path: '/pong/',
        template: async () => {
            return await fetchRoute('/pages/pong/');
        },
    },
    {
        path: '/admin/',
        template: async () => {
            return await fetchRoute('/pages/admin/');
        },
    },
    {
        path: '/auth/register',
        template: async () => {
            return await fetchRoute('/pages/auth/register');
        },
    },
    {
        path: '/error/404/',
        template: async () => {
            return await fetchRoute('/pages/error/404/');
        },
    },
    {
        path: '/pong/gamemodes/',
        template: async () => {
            return await fetchRoute('/pages/pong/gamemodes/');
        },
    },
    {
        path: '/pong/arena/',
        template: async () => {
            return await fetchRoute('/pages/pong/arena/');
        },
    },
    {
        path: '/pong/matchmaking/',
        template: async () => {
            return await fetchRoute('/pages/pong/matchmaking/');
        },
    },
    {
        path: '/chat/',
        template: async () => {
            return await fetchRoute('/pages/chat/');
        },
    },
    {
        path: '/profile/settings/',
        template: async () => {
            return await fetchRoute('/pages/profile/settings/');
        },
    },
    {
        path: '/profile/',
        template: async (query) => {
            console.log(`/pages/profile/${query}`)
            return await fetchRoute(`/pages/profile/${query}`);
        }
    },
    {
        path: '/auth/2fa',
        template: async () => {
            return await fetchRoute('/pages/auth/2fa');
        },

    },
    {
        path: '/pong/gameover/',
        template: async (query) => {
            console.log(`/pages/profile/${query}`)
            return await fetchRoute(`/pages/pong/gameover/${query}`);
        },
    },
    {
        path: '/auth/auth42',
        template: async (query) => {
            console.log(`/pages/auth/auth42`, query)
            console.log("gigaMEOOOWWWWWW")
            return await fetchRoute(`/pages/auth/auth42${query}`);
        },
    },
    {
        path: '/admin/monitoring/',
        template: async (query) => {
            console.log(`/pages/profile/${query}`)
            return await fetchRoute(`/pages/admin/monitoring/`);
        },
    },
    {
        path: '/chat/friendrequest/',
        template: async () => {
            return await fetchRoute(`/pages/chat/friendrequest/`);
        },
    },
    {
        path: '/pong/disconnect/',
        template: async () => {
            return await fetchRoute(`/pages/pong/disconnect/`);
        },
    }
];

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    const routeElement = e.target.closest('[data-route]');
    if (routeElement) {
        const route = routeElement.dataset.route;
        // console.log("in data route :", route);
        navigateTo(route);
    }
});


const router = new Router(routes);

document.addEventListener("keypress", function(event) {
    const routeElement = event.target.closest('.searchBar');
    if (event.key === "Enter")
    {
        if (routeElement)
        {
            event.preventDefault();
            const inputElement = routeElement.querySelector('input');
            let query = inputElement.value;
            navigateTo('/profile/?username=' + query)
            inputElement.value = '';
        }
    }
})


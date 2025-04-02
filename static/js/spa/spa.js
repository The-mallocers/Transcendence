import { WebSocketManager } from "../websockets/websockets.js"
import { isGameOver } from "../apps/game/VarGame.js"


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
        
        const path = window.location.pathname;

        console.log(window.location.search);
        console.log("looking for the path: ", path)
        const route = this.routes.find(r => r.path === path);

        if (!route) {
            navigateTo("/error/404/");
        }
        else {
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
        if( splitedPath.includes("pong")) {
            WebSocketManager.closeChatSocket();
        }
        else {
            WebSocketManager.closeAllSockets(); //for now we close all
        }
        if (window.location.pathname == path) {return ;}
        
        isGameOver.gameIsOver = true;
        //In the future, we will have to do some better logics with the path to decide if we want to close
        //a websocket or not.
        
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

window.onload = async ()=>{
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
    const response = await fetch(path, {
        headers: header,
        credentials: 'include'
    });
    const data = await response.json();
    // console.log("testing redirect, data is :", data)
    if (response.ok) {
        console.log("response is A ok")
        return data.html;
    }
    else if (response.status === 302) {
        //redirection
        path = '/pages/auth/login'
        const response = await fetch(path, {
            headers: header,
            credentials: 'include'
        });
        const data = await response.json();
        window.history.pushState({}, '', '/auth/login');
        return data.html
    }
    else if (response.status >= 400 && response.status < 500) 
    {
        return data.html;

    }
    else if (response.status == 500) {
        //do something special
    }
    else {
        console.log("error, this isnt a valid error handling, but what do you want me to do")
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
];

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    const routeElement = e.target.closest('[data-route]');
    if (routeElement) {
        const route = routeElement.dataset.route;
        console.log("in data route :", route);
        navigateTo(route);
    }
});


const router = new Router(routes);

class Route{
    constructor(route, directSubRoutes){
        this.route = route
        this.directSubRoutes = directSubRoutes.map(sub => new Route(sub.route, sub.directSubRoutes))
    }


    get possibleRoutes(){
        let routes = [this.route];
        for (let subRoute of this.directSubRoutes) {
            const subRoutes = subRoute.possibleRoutes.map(r => this.route + r);
            routes = routes.concat(subRoutes);
        }
        return routes;
    }
}


const pongRoute = new Route(
    '/pong',
    [
        {
            route: '/test1',
            directSubRoutes : []
        },
        {
            route: '/test2',
            directSubRoutes : []
        },        {
            route: '/test3',
            directSubRoutes : [
                {
                    route: '/meow',
                    directSubRoutes : []
                }
            ]
        }
    ]
    
)

//create socker for notifications
let client_id = null;
const clientId = await getClientId();
const notifSocket = new WebSocket(`wss://${window.location.host}/ws/notification/?id=${clientId}`);

async function getClientId() {
    // if (client_id !== null) return client_id;
    console.log("Getting client ID")
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();

        if (data.client_id) {
            client_id = data.client_id;
            return client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

notifSocket.onmessage = (event) => {
    console.log(event.data);
    const message = JSON.parse(event.data);
    
    if(message.data.action == "ACK_SEND_FRIEND_REQUEST") {
        let pending_group = document.querySelector('.pending_group');
        const parser = new DOMParser();
        const htmlString = 
        `<li class="list-group-item pending_item d-flex justify-content-between align-items-center" id="${message.data.content.username}">
            ${message.data.content.username}
            <div class="btn-group d-grid gap-2 d-md-flex justify-content-md-end"  role="group" aria-label="Basic example">
                <button type="button" class="type-intra-green accept_friend" data-username="${message.data.content.username}">accept</button>
                <button type="button" class="type-intra-white refuse_friend" data-username="${message.data.content.username}">refuse</button>
            </div>
        </li>
        `
        const doc = parser.parseFromString(htmlString, "text/html");
        const pendingElement = doc.body.firstChild;
        pending_group.appendChild(pendingElement);
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST_HOST") {
        let friends_group = document.querySelector('.friends_group');
        const parser = new DOMParser();
        const add_to_friend = 
        `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${message.data.content.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green delete_friend me-4" data-username="${message.data.content.username}" >delete</button>
                <span>14</span>
            </div>
        </li>
        `
        const doc = parser.parseFromString(add_to_friend, "text/html");
        const friendElement = doc.body.firstChild;
        friends_group.appendChild(friendElement);
        const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
        console.log(buttonToDelete);
        console.log(message.data.content.username);
        if(buttonToDelete)
        {
            buttonToDelete.remove();
        }
    }
    else if(message.data.action == "ACK_ACCEPT_FRIEND_REQUEST") {
        let friends_group = document.querySelector('.friends_group');
        const parser = new DOMParser();
        const add_to_friend = 
        `<li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${message.data.content.username}</div>
            <div class="d-flex align-items-center">
                <button type="button" class="type-intra-green delete_friend me-4" data-username="${message.data.content.username}" >delete</button>
                <span>14</span>
            </div>
        </li>
        `
        const doc = parser.parseFromString(add_to_friend, "text/html");
        const friendElement = doc.body.firstChild;
        friends_group.appendChild(friendElement);
    }
    else if(message.data.action == "ACK_REFUSE_FRIEND_REQUEST") {
        const buttonToDelete = document.querySelector(`li.pending_item#${message.data.content.username}`);
        console.log(buttonToDelete);
        console.log(message.data.content.username);
        if(buttonToDelete)
        {
            buttonToDelete.remove();
        }
    }
    else if(message.data.action == "ACK_DELETE_FRIEND") {
        const friendElements = document.querySelectorAll('.friends_group li');
        friendElements.forEach(elem => {
            const usernameElement = elem.querySelector('div:first-child');
            if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
                elem.remove();
            }
        });
    }
    else if(message.data.action == "ACK_FRIEND_DELETED_HOST") {
        const friendElements = document.querySelectorAll('.friends_group li');
        friendElements.forEach(elem => {
            const usernameElement = elem.querySelector('div:first-child');
            if (usernameElement && usernameElement.textContent.trim() === message.data.content.username) {
                elem.remove();
            }
        });
}}

document.addEventListener("click", function(event) {
    const routeElement = event.target.closest('.friendrequest');
    const acceptFriend = event.target.closest('.accept_friend');
    const refuseFriend = event.target.closest('.refuse_friend');
    const deleteFriend = event.target.closest('.delete_friend');

    const urlParams = new URLSearchParams(window.location.search);
    if (routeElement) {
        const targetUser = urlParams.get('username');
        console.log("the firend to add is " + targetUser)
        this.value = ""; // Clear the input field after handling
        const message = create_message("send_friend_request", targetUser);
        console.log(message);
        notifSocket.send(JSON.stringify(message));
        navigateTo('/')
    }
    else if(acceptFriend)
    {
        console.log("accept friend");
        const targetUser = acceptFriend.dataset.username;
        this.value = ""; // Clear the input field after handling
        const message = create_message("accept_friend_request", targetUser)
        notifSocket.send(JSON.stringify(message));
    }
    else if(refuseFriend)
    {
        const targetUser = refuseFriend.dataset.username;
        this.value = ""; // Clear the input field after handling
        const message = create_message("refuse_friend_request", targetUser);
        notifSocket.send(JSON.stringify(message));
    }
    else if(deleteFriend)
    {
        const targetUser = deleteFriend.dataset.username;
        this.value = ""; // Clear the input field after handling
        const message = create_message("delete_friend", targetUser);
        notifSocket.send(JSON.stringify(message));
    }
});

function create_message(action, targetUser)
{
    let message = {
        "event": "notification",
        "data": {
            "action": action,
            "args": {
                "target_name": targetUser,
            }
        } 
    }
    return message;
}

document.addEventListener("keypress", function(event) {
    const routeElement = event.target.closest('.searchBar');
    console.log(routeElement);
    if (event.key === "Enter")
    {
        if (routeElement)
        {
            event.preventDefault();
            const inputElement = routeElement.querySelector('input');
            let query = inputElement.value;
            navigateTo('/profile/?username=' + query)
        }
    }
})
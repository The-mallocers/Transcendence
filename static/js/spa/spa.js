// console.log("ALLOO :", window.location.pathname);

import { logout } from '../apps/auth/logout.js';
// import { login } from '../apps/auth/login.js';
import { register } from '../apps/auth/register.js';

let previous_route = null;


class Router {
    constructor(routes) {
        this.routes = routes;
        this.rootElement = document.getElementById('app');
        this.init();
    }
    //Claude said the above method is better than : document.querySelector('#app');
    init() {
        window.addEventListener('popstate', () => this.handleLocation());
        //this.handleLocation();
    }

    async handleLocation() {
        const path = window.location.pathname;
        console.log("looking for the path: ", path)
        const route = this.routes.find(r => r.path === path);
        if (!route) {
            navigateTo("/error/404/");
        }
        else {
            try {
                // console.log("About to try the route template of the route :", route);
                console.log("checking out previous route and events");
                console.log(previous_route);
                if (previous_route != null) {
                    console.log(previous_route.events);
                    previous_route.events.forEach(element => {
                        document.getElementById(element.id).removeEventListener(element.event_type, element.func)
                        console.log("removed my event handler like a boss");
                        console.log(element.event_type)
                    });
                };
                const content = await route.template();
                this.rootElement.innerHTML = content;
                console.log("Reloading Scripts", this.rootElement);
                // Dispatch a custom event
                const pageLoadEvent = new CustomEvent('SpaLoaded', {
                    detail: { path: path, funct: this.reloadScripts, events: route.events }
                });
                console.log("");
                document.dispatchEvent(pageLoadEvent);
                previous_route = route; //Updating previous path so that next time it exists
                // this.reloadScripts();
            } catch (error) {
                console.error('Route rendering failed:', error);
            }
        }
    }

    reloadScripts() {
        // Execute all scripts in the new content
        console.log("RELOADED", this.rootElement)
        const scripts = this.rootElement.querySelectorAll('script');
        console.log("scripts = ", scripts)
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            
            // Copy src or inline content
            if (oldScript.src) {
                newScript.src = oldScript.src;
                console.log("hello, newscript.src :", newScript.src)
            } else {
                newScript.textContent = oldScript.textContent;
            }
            
            // Copy other attributes
            Array.from(oldScript.attributes).forEach(attr => {
                if (attr.name !== 'src') { // Skip src as we handled it above
                    newScript.setAttribute(attr.name, attr.value);
                    console.log("new script attribute = ", attr.name, attr.value)
                }
            });
            
            // Replace old script with new one
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }

    navigate(path) {
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

window.onload = async ()=>{
    console.log(pongRoute.possibleRoutes)
    // console.log(window.location.pathname)
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
    console.log("testing redirect, data is :", data)
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
            // console.log("I am fetching a route in spa.js")
            return await fetchRoute('/pages/');
        },
    },
    {
        path: '/auth/login',
        events: [{
            id: 'login-btn',
            event_type: 'click',
            func: login
        },],
        template: async () => {
            return await fetchRoute('/pages/auth/login');
        },
    },
    {
        path: '/pong/',
        template: async () => {
            // console.log("fetching pong")
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
        path: '/auth/2fa',
        template: async () => {
            return await fetchRoute('/pages/auth/2fa');
        },
    },
];

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    // console.log("click !")
    // console.log(e);
    const routeElement = e.target.closest('[data-route]');
    if (routeElement) {
        const route = routeElement.dataset.route;
        console.log("in data route :", route);
        navigateTo(route);
    }
    //this may not look like it but this took a very long time to come up with
    if (e.target.matches('#logout-btn') || e.target.closest('#logout-btn')) {
        logout();
    }
    // if (e.target.matches('#login-btn') || e.target.closest('#login-btn')) {
    //     login(e);
    // }
    if (e.target.matches('#register-btn') || e.target.closest('#register-btn')) {
        register(e);
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

/// routes

/*
    example objects skeleton: {
        route: -------,
        directSubRoutes: [{route object}]
    }
*/



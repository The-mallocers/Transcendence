console.log("ALLOO :", window.location.pathname);


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
            this.rootElement.innerHTML = `<div style="text-align: center; padding: 50px;">
                    <h1>404 - Page Not Found</h1>
                    <p>Sorry, the page you are looking for does not exist.</p>
                </div>`;
        }
        else {
            try {
                const content = await route.template();
                this.rootElement.innerHTML = content;
                this.reloadScripts();
            } catch (error) {
                console.error('Route rendering failed:', error);
            }
        }
    }

    reloadScripts() {
        // Execute all scripts in the new content
        const scripts = this.rootElement.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            
            // Copy src or inline content
            if (oldScript.src) {
                newScript.src = oldScript.src;
            } else {
                newScript.textContent = oldScript.textContent;
            }
            
            // Copy other attributes
            Array.from(oldScript.attributes).forEach(attr => {
                if (attr.name !== 'src') { // Skip src as we handled it above
                    newScript.setAttribute(attr.name, attr.value);
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
    // console.log(pongRoute.possibleRoutes)
    console.log(window.location.pathname)
    await router.handleLocation();
}

// Navigation helper
export function navigateTo(path) {
    router.navigate(path);
}

function getToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];
}

// Example route definitions
const header = {
    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    'X-Requested-With': 'XMLHttpRequest',
};

async function fetchRoute(path) {
    // console.log("trying to print my cookies :", document.cookie)
    // console.log("Trying to print the access token specifically")
    // console.log(getToken());
    const response = await fetch(path, {
        headers: header,
        credentials: 'include'
    });
    const data = await response.json();
    alert("hein")
    console.log("testing redirect, data is :", data)
    if (response.ok) {
        return data.html;
    }
    else {
        console.log("in the else", data)
        // navigateTo(response.redirect)
    }
}

const routes = [
    {
        path: '/',
        template: async () => {
            console.log("I am fetching a route in spa.js")
            return await fetchRoute('/pages');
        },
    },
    {
        path: '/auth/login',
        template: async () => {
            return await fetchRoute('/pages/auth/login');
        },
    },
    {
        path: '/auth/register',
        template: async () => {
            return await fetchRoute('/pages/auth/register');
        },
    },
];

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', (e) => {
    if (e.target.matches('[data-route]')) {
        const route = e.target.dataset.route;
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

/// routes

/*
    example objects skeleton: {
        route: -------,
        directSubRoutes: [{route object}]
    }
*/



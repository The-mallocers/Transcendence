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
        this.handleLocation();
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
                // route.script && route.script();
            } catch (error) {
                console.error('Route rendering failed:', error);
            }
        }
    }

    navigate(path) {
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

window.onload = async ()=>{
    console.log(pongRoute.possibleRoutes)
    console.log(window.location.pathname)
    await router.handleLocation();
}

// Navigation helper
function navigateTo(path) {
    router.navigate(path);
}

// Example route definitions
const routes = [
    {
        path: '/',
        template: async () => {
            const response = await fetch('pages/', {
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            const data = await response.json();
            return data.html;
        },
    },
    {
        path: 'pages/auth/login',
        template: async () => {
            const response = await fetch('pages/auth/login', {
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            const data = await response.json();
            return data.html;
        },
    },
];

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
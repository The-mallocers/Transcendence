// static/js/router.js
class Router {
    constructor(routes) {
        this.routes = routes;
        this.rootElement = document.getElementById('app');
        this.init();
    }

    init() {
        window.addEventListener('popstate', () => this.handleLocation());
        this.handleLocation();
    }

    async handleLocation() {
        const path = window.location.pathname;
        const route = this.routes.find(r => r.path === path) || this.routes[0];
        
        try {
            const content = await route.template();
            this.rootElement.innerHTML = content;
            route.script && route.script();
        } catch (error) {
            console.error('Route rendering failed:', error);
        }
    }

    navigate(path) {
        window.history.pushState({}, '', path);
        this.handleLocation();
    }
}

// Example route definitions
const routes = [
    {
        path: '/',
        template: async () => {
            const response = await fetch('/pong/');
            const data = await response.text();
            console.log(data);
            return data;
        },
        script: () => {
            // Page-specific JavaScript
            console.log('Home page loaded');
        }
    },  
];

const router = new Router(routes);

// Navigation helper
function navigateTo(path) {
    router.navigate(path);
}
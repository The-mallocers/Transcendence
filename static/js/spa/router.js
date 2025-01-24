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
        const route = this.routes.find(r => r.path === path); //|| this.routes[0];
        
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
    // {
    //     path: '/',
    //     template: async () => {
    //         const response = await fetch('/pong/');
    //         const data = await response.text();
    //         console.log(data);
    //         return data;
    //     },
    //     script: () => {
    //         // Page-specific JavaScript
    //         console.log('Home page loaded');
    //     }
    // },
    {
        path: '/partial/1',
        template: async () => {
            const response = await fetch('/spa/partial/1');
            const data = await response.text();
            return data;
        },
        script: () => {
            console.log('partial loaded like a boss')
        }
    },    {
        path: '/partial/2',
        template: async () => {
            const response = await fetch('/spa/partial/2');
            const data = await response.text();
            return data;
        },
        script: () => {
            console.log('partial loaded like a boss')
        }
    },    {
        path: '/partial/3',
        template: async () => {
            const response = await fetch('/spa/partial/3');
            const data = await response.text();
            return data;
        },
        script: () => {
            console.log('partial loaded like a boss')
        }
    }
];

const router = new Router(routes);

//Below is the actual that works

// Navigation helper
function navigateTo(path) {
    router.navigate(path);
}

//Below is my attempt at giving content without changing the url
// async function navigateTo(path) {
//     console.log(path)
//     const response = await fetch(path);
//     const data = await response.text();
//     return data;
// }


let p1 = document.getElementById("part1")
let p2 = document.getElementById("part2")
let p3 = document.getElementById("part3")


p1.addEventListener('click', async (e)=>{
    navigateTo(e.target.dataset.url)
})
p2.addEventListener('click', (e)=>{
    navigateTo(e.target.dataset.url)
})
p3.addEventListener('click', (e)=>{
    navigateTo(e.target.dataset.url)
})
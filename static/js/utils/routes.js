import {fetchRoute} from "../spa/spa.js";

const routes = [
    // Ajoute ta route avec pas basique la bg
    {
        path: '/profile/',
        template: async (query) => {
            return await fetchRoute(`/pages/profile/${query}`);
        }
    },
    {
        path: '/pong/gameover/',
        template: async (query) => {
            return await fetchRoute(`/pages/pong/gameover/${query}`);
        }
    },
    {
        path: '/auth/auth42',
        template: async (query) => {
            return await fetchRoute(`/pages/auth/auth42${query}`);
        }
    },

    // Ajoute ta route basique la bg !
    '/',
    '/auth/login',
    '/pong/',
    '/admin/',
    '/auth/register',
    '/error/404/',
    '/pong/gamemodes/',
    '/pong/arena/',
    '/pong/matchmaking/',
    '/chat/',
    '/profile/settings/',
    '/auth/2fa',
    '/admin/monitoring/',
    '/chat/friendrequest/',
    '/pong/disconnect/'
].map(route => {
    if (typeof route === 'object') return route;

    return {
        path: route,
        template: async () => {
            return await fetchRoute(`/pages${route}`);
        }
    };
});

export {routes}
import routes from './routes.js';

function navigateTo(path) {
    history.pushState({}, '', path);
    renderPage(path);
}

function renderPage(path) {
    const route = routes.find(route => route.path === path);
    if (route) {
        document.getElementById('app').innerHTML = route.component();
    } else {
        document.getElementById('app').innerHTML = '<h1>404 - Page Not Found</h1>';
    }
}

// Listen for browser navigation events
window.addEventListener('popstate', () => renderPage(window.location.pathname));

export default navigateTo;
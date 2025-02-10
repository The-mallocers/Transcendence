import navigateTo from './router/router.js';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    navigateTo(window.location.pathname);
    console.log("testttttt")
    // Example navigation setup
    document.body.addEventListener('click', (e) => {
        if (e.target.matches('[data-link]')) {
            e.preventDefault();
            navigateTo(e.target.href);
        }
    });
});
import { navigateTo } from '../../spa/spa.js';


export function logout() {
    console.log("logout.js online")
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, 
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})  // sending an empty body for some reasons
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Logout successful:', data);
            navigateTo('/auth/login')
        })
        .catch(error => {
            console.error('Error during logout:', error);
    });
};
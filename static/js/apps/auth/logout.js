import { navigateTo } from '../../spa/spa.js';


export function logout() {
    console.log("logout.js online")
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,  // Inclus le CSRF token
            'Content-Type': 'application/json'  // Type de contenu JSON même si aucune donnée n'est envoyée
        },
        body: JSON.stringify({})  // Envoi d'un corps vide
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();  // Si vous attendez une réponse JSON
        })
        .then(data => {
            console.log('Logout successful:', data);
            // Vous pouvez rediriger ou afficher un message de succès ici
            navigateTo('/auth/login')
        })
        .catch(error => {
            console.error('Error during logout:', error);
    });
};
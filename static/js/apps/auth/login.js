import { navigateTo } from '../../spa/spa.js';

console.log("Loaded the dom in login.js")
// Sélectionner le formulaire et ajouter un événement de soumission
const form = document.querySelector("form");

// Empêcher le comportement de soumission par défaut
form.addEventListener("submit", function (event) {
    event.preventDefault();

    // Récupérer les données du formulaire
    const formData = new FormData(form);
    const errorDiv = document.getElementById("error-message")

    console.log("About to fetch : ", form.action);
    // Utilisation de l'API Fetch pour envoyer les données
    fetch(form.action, {
        method: "POST",  // Méthode de la requête (POST)
        body: formData,  // Corps de la requête (les données du formulaire)
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
        .then(response => response.json())  // Réponse en JSON
        .then(data => {
            if (data.success) {
                // Si la soumission est réussie, vous pouvez afficher un message ou rediriger l'utilisateur
                alert("Yo la team jsuis dans le js de login")
                console.log("data", data)
                console.log("allo ?")
                navigateTo('/');
                return
                // window.location.href = '/';  // Redirige si une URL de redirection est fournie
            } else {
                // En cas d'erreur, afficher un message d'erreur
                errorDiv.textContent = data.message;
            }
        })
        .then((ZEBI => {
                const allCookies = document.cookie;
                console.log(allCookies);
        }))
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
            errorDiv.textContent = error;
        });
});
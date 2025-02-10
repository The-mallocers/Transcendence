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

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
        .then(response => {
            if (response.ok) {
                navigateTo('/');
            }
            else {
                response.json().then(errorData => {
                    errorDiv.textContent = errorData.error || "An error occurred";
                });
            }
        })
        .catch(error => {
            console.error("There was an error with the fetch operation:", error);
            errorDiv.textContent = "Error, please check your internet and try again later";
        });
});
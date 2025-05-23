document?.addEventListener("DOMContentLoaded", function () {
    // Sélectionner le formulaire et ajouter un événement de soumission
    const form = document.querySelector("form");
    const button_delete = document.getElementById("delete-account-btn");

    // Empêcher le comportement de soumission par défaut
    form?.addEventListener("submit", function (event) {
        event.preventDefault();

        // Récupérer les données du formulaire
        const formData = new FormData(form);

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
                    window.location.href = '/';  // Redirige si une URL de redirection est fournie
                } else {
                    // En cas d'erreur, afficher un message d'erreur
                    alert("Error: " + data.message);
                }
            })
            .catch(error => {
                console.error("There was an error with the fetch operation:", error);
            });
    });

    button_delete?.addEventListener("click", function (event) {
        event.preventDefault();  // Empêche le comportement par défaut du bouton
        event.stopPropagation(); // Empêche la propagation de l'événement
        if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            fetch('/api/account/', {
                method: "DELETE",  // Méthode de la requête (POST)
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
                .then(response => response.json())  // Réponse en JSON
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        // Si la soumission est réussie, vous pouvez afficher un message ou rediriger l'utilisateur
                        window.location.href = '/auth/login';  // Redirige si une URL de redirection est fournie
                    } else {
                        // En cas d'erreur, afficher un message d'erreur
                        alert("Error: " + data.message);
                    }
                })
                .catch(error => {
                    console.error("There was an error with the fetch operation:", error);
                });
        }
    })
});
document.addEventListener("DOMContentLoaded", function () {
    const addUserBtn = document.getElementById('add-user-btn');
    const addUserPopup = document.getElementById('add-user-popup');
    const addUserForm = document.getElementById('add-user-form');

    // Afficher le popup pour ajouter un utilisateur
    addUserBtn.addEventListener("click", function () {
        addUserPopup.style.display = 'flex';
    });

    // Fermer le popup
    function closePopup() {
        addUserPopup.style.display = 'none';
    }

    // Soumettre le formulaire pour ajouter un utilisateur
    addUserForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(addUserForm);

        fetch('/api/auth/register', {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("User added successfully!");
                    window.location.reload(); // Recharger la page pour afficher le nouvel utilisateur
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });

    // Fonction pour supprimer un utilisateur
    function deleteUser(userId) {
        if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            fetch(`/api/account/delete/${userId}`, {
                method: "DELETE",
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        window.location.reload(); // Recharger la page après suppression
                    } else {
                        alert("Error: " + data.message);
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                });
        }
    }

    // Fonction pour fermer le popup
    window.closePopup = closePopup;
    window.deleteUser = deleteUser;
});
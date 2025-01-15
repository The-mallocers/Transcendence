document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("register-form");
    const errorMessageDiv = document.getElementById("error-message");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire

        // Récupération des valeurs des champs
        const first_name = document.getElementById("first_name").value;
        const last_name = document.getElementById("last_name").value;
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const password_check = document.getElementById("password_check").value;

        if (password !== password_check)
        {
            errorMessageDiv.textContent = "Les mots de passe ne correspondent pas"
            return;
        }

        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/api/auth/register", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    first_name: first_name,
                    last_name: last_name,
                    username: username,
                    email: email,
                    password: password,
                    password_check: password_check
                }),
            });

            const result = await response.json();

            if (response.status === 200) {
                window.location.href = '/';
            }
            else{
                errorMessageDiv.textContent = result.message || "Échec de l'inscription.";
            }
        } catch (error) {
            console.error("Erreur lors de la connexion :", error);
            errorMessageDiv.textContent = "Une erreur s'est produite. Veuillez réessayer.";
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("register-form");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire

        // Récupération des valeurs des champs
        const first_name = document.getElementById("first_name").value;
        const last_name = document.getElementById("last_name").value;
        const nickname = document.getElementById("nickname").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const password_verif = document.getElementById("password_verif").value;

        if (password !== password_verif)
        {
            alert("Password missmatch" || "Error")
            return;
        }

        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/auth/register", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    first_name: first_name,
                    last_name: last_name,
                    nickname: nickname,
                    email: email,
                    password: password,
                    password_verif: password_verif
                }),
            });

            const result = await response.json();

            if (response.status === 200 && result.success){
                window.location.href = result.redirect_url;
            }
            else{
                alert(result.message || "Login failed.");
            }
        } catch (error) {
            console.error("Erreur lors de la connexion :", error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
});
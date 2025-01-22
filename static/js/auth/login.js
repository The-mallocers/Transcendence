document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire

        // Récupération des valeurs des champs
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/api/auth/login", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            });
            
            const result = await response.json();

            if (response.status === 200 && result.success){
                console.log(result.redirect_url);
                // window.location.href = result.redirect_url;
                window.location.href = "/"
            }
            else{
                alert(result.message || "Login failed.");
                window.location.href = "/auth/register"
            }
        } catch (error) {
            console.error("Erreur lors de la connexion :", error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
});
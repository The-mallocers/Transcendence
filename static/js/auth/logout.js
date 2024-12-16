document.addEventListener("DOMContentLoaded", function () {
    const logoutForm = document.getElementById("logout-form");

    logoutForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire

        // Récupération des valeurs des champs
        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/auth/logout", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                }),
            });

            const result = await response.json();

            if (response.status === 200 && result.success){
                alert(result.message || "You are log out")
                window.location.href = result.redirect_url;
            }
        } catch (error) {
            console.error("Erreur lors de la connexion :", error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
});
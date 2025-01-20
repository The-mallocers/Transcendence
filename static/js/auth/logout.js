function getCsrfTokenFromCookies() {
    const match = document.cookie.match(new RegExp('(^| )csrf_token=([^;]+)'));
    return match ? match[2] : null;
}

document.addEventListener("DOMContentLoaded", function () {
    const logoutForm = document.getElementById("logout-form");

    logoutForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire
        const csrfToken = getCsrfTokenFromCookies();

        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/api/auth/logout", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken
                },
                body: JSON.stringify({
                }),
            });

            const result = await response.json();

            if (response.status === 200 && result.success){
                window.location.href = '/auth/login';
            }
        } catch (error) {
            console.error("Erreur lors de la connexion :", error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
});
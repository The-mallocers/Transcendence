document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire

        const formData = new FormData(form);
        const errorDiv = document.getElementById("error-message")

        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/api/auth/login", { // Remplace "/login" par l'URL de ton endpoint
                method: "POST",
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            });
            const result = await response.json();

            if (response.status === 200 && result.success){
                window.location.href = result.redirect_url;
            }
            else{
                alert(result.message || "Login failed.");
                window.location.href = "/auth/register"
            }
        } catch (error) {
            console.error(error);
            errorDiv.textContent = error;
        }
    });
});

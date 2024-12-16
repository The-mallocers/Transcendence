const user = async (form) => {
    const input = form.querySelectorAll("input")[0];
    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Empêche le rechargement de la page lors de l'envoi du formulaire
        // Récupération des valeurs des champs
        try {
            // Envoi de la requête POST avec fetch
            const response = await fetch("/account/", { // Remplace "/login" par l'URL de ton endpoint
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "data": input.id,
                    "value": input.value
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
}

const formsContainer = document.getElementById("account-container");
const forms = formsContainer.querySelectorAll("form");
for (let i = 0; i < forms.length; i++) {
    user(forms[i]).then(r => "");
}
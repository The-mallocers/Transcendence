document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const error = document.getElementById("error-message");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                window.location.href = '/';
                } else {
                    error.textContent = data.message
            }
            })
            .catch(error => {
                console.error("There was an error with the fetch operation:", error);
            });
    });
});
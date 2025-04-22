const upload_btn = document.getElementById("upload-img-btn");
const file_input = document.getElementById('file_input');
upload_btn.addEventListener('click', () =>  {
    file_input.click();
});


file_input.addEventListener('change', async () => {
    const file = file_input.files[0];
    if (file) {
        try {
            const formData = new FormData();
            formData.append('profile_picture', file);

            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const response = await fetch("/api/auth/upload_picture/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData 

            });
            const data = await response.json();
            if (response.ok) {
                showFeedback("Profile picture uploaded successfully!");
            }
            else {
                showFeedback(data?.profile_picture?.[0] || "Something went wrong.", false);
            }
        } catch (error) {
            const errorMessage = "Something went wrong, please upload a valid image 1000x1000 at most";
            showFeedback(errorMessage, false);
        }
    }
});

const feedback = document.getElementById("upload-feedback");

function showFeedback(message, isSuccess = true) {
    if (isSuccess) {
        feedback.innerHTML = message;
        feedback.style.color = "#28a745"; // Green color
        feedback.style.fontWeight = "bold";
    }
    else {
        //The error message was a bit ugly
        const regex = /string='([^']+)'/;
        const match = message.match(regex);

        if (match && match[1]) {
            feedback.innerHTML =  match[1];
        } else {
            feedback.innerHTML =  message;
        }
        feedback.style.color = "#dc3545"; 
        feedback.style.fontWeight = "bold"; 
    }
}
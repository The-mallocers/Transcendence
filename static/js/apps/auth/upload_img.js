import * as html from "../../utils/html_forms.js"

const upload_btn = document.getElementById("upload-img-btn");
const file_input = document.getElementById('file_input');
upload_btn.addEventListener('click', () =>  {
    file_input.click();
});


file_input.addEventListener('change', async () => {
    const file = file_input.files[0];
    //Do I add the validation here ?
    //Client AND server side validation like a BOSS;
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
                //Update something in the html to show we uploaded the image succesfully;
                console.log("You uploaded the image !");
            }
            else {
                console.log("There was an error trying to upload the image");
                console.log(data); // Log the error details
                //Maybe do something different depending on if the image is too small or if the image is not a png
            }
        } catch (error) {
            console.error(error.message);
            return html.Fetch_Error;
        }
    }
});
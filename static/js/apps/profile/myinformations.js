console.log("in the myinformations file");

window.switchToggle = async function switchToggle(e) {
    e.dataset.status = (e.dataset.status === 'on' ? 'off' : 'on');
    let bool_2fa = false;
    // Target the SVG using its class name and change the fill color
    if (e.dataset.status === 'on') {
        document.querySelector(".shieldPath").classList.add("fillGreen");
        bool_2fa = true;
    } else {
        bool_2fa = false;
        document.querySelector(".shieldPath").classList.remove("fillGreen");
    }
    const response = await fetch("/api/auth/change_two_fa", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            status: bool_2fa,
        }),
    });
    if(response.status === 200)
    {
        const res = await response.json();
        if(res.state == true){
            console.log(res.image);
            create_modal(res);
        }
        console.log(response);
    }
}

function create_modal(res){
    const image = res.image;
    const parser = new DOMParser();
    const htmlContent = `
    <div class="modal fade" id="twoFactorModal" tabindex="-1" aria-labelledby="twoFactorModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content d-flex">
                <div class="modal-header">
                    <h5 class="modal-title" id="twoFactorModalLabel">Two FA Authentification</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="align-self-center">
                    <img class="twofa-image" src="${image}" alt="2FA QR Code">
                </div>
                <div class="align-self-center">
                    <form id="twoFactorForm" class="d-flex flex-column align-items-center">
                        <input class="twofa-input"
                            type="text"
                            id="authCode"
                            maxlength="6"
                            placeholder="Enter 6-digit code"
                            pattern="[0-9]{6}"
                            required>
                        <br>
                        <button class="type-intra-green verify-code" type="submit">Verify Code</button>
                    </form>
                </div>
            </div>
        </div>
    </div>`
    const doc = parser.parseFromString(htmlContent, "text/html");
    const modalElement = doc.body.firstChild;
    document.body.appendChild(modalElement);

    document.getElementById("twoFactorForm").addEventListener("submit", function(event) {
        event.preventDefault();
        validateCode();
    });

    const modal = new bootstrap.Modal(document.getElementById('twoFactorModal'));
    modal.show();
}

async function validateCode() {
    const code = document.getElementById('authCode').value;
    if (code.length === 6 && /^\d+$/.test(code)) {
        try {
            const response = await fetch("/api/auth/check2faqrcode", {
                method: "POST",
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: JSON.stringify({
                    code: code,
                    email: email
                }),
            });

            const result = await response.json();
            if (response.status === 200 && result.success) {
                navigateTo(result.redirect); //make sure to change to redirect
            }
            else{
                alert(`${result.message}`)
            }
        } catch (err) {
            navigateTo(result.redirect);
        }
    } else {
        alert('Please enter a valid 6-digit code');
    }
}
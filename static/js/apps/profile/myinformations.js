let enable = false;


document.getElementById('twoFactorModal')?.addEventListener('hidden.bs.modal', function () {
    const switchElement = document.querySelector('.switch');
    let currentState = switchElement.getAttribute('data-status');
    if(enable == false && currentState == "on"){
        switchElement.setAttribute('data-status', "off");
        switchElement.classList.remove("fillGreen");
        document.querySelector(".shieldPath").classList.remove("fillGreen");
        enable = false;
    }
})

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
            create_modal(res);
        }
    }
}

function create_modal(res){
    const image = res.image;
    
    const imageElement = document.querySelector(".twofa-image");
    if(imageElement)
        imageElement.src = image;
    enable = false;
    const modalElement = document.getElementById('twoFactorModal');
    modalElement?.addEventListener('shown.bs.modal', function () {
        // Focus on the input field
        document.getElementById('authCode').focus();
    }, { once: true }); 
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
                }),
            });

            const result = await response.json();
            if (response.status === 200 && result.success) {
                alert("2fa successfully implemented");
                hide_modal();
                enable = true;
            }
            else{
                alert(`${result.message}`)
                const input = document.getElementById('authCode');
                if (input)
                    input.value = "";
            }
        } catch (err) {
            alert(`${err.message}`)
            hide_modal();
        }
    } else {
        alert('Please enter a valid 6-digit code');
    }
}

function hide_modal(){
    const input = document.getElementById('authCode');
    if (input)
        input.value = "";
    const modal = bootstrap.Modal.getInstance(document.getElementById('twoFactorModal'));
    if(modal)
        modal.hide();
}

const modalKeyElement = document.getElementById('twoFactorModal');
modalKeyElement?.addEventListener('hide.bs.modal', () => {
    if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur();
    }
});

window.validateCode = validateCode;
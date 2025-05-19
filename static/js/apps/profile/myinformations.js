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
    // console.log("crsf token is : ", document.querySelector('[name=csrfmiddlewaretoken]').value)
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
}

async function switchToggle(e) {
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
    // console.log("crsf token is : ", document.querySelector('[name=csrfmiddlewaretoken]').value)
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
}
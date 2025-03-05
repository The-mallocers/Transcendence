import { navigateTo } from '../../spa/spa.js';

const email = document.getElementById("data-email").getAttribute("email");

async function validateCode() {
	const code = document.getElementById('authCode').value;
	if(code.length === 6 && /^\d+$/.test(code)) {
		// Here you would typically send the code to your server for validation
		try{
			console.log(code);
			const response = await fetch("/api/auth/2facode", { //added api as this is an api call
				method: "POST",
				headers: {
					'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
				},
				body: JSON.stringify({
					code : code,
					email: email
				}),
			});
			
			const result = await response.json();
			console.log(result);
			if(response.status === 200 && result.success)
			{
				navigateTo(result.redirect); //make sure to change to redirect
				// window.location.href = result.redirect_url;
			}
			alert('Code submitted: ' + code);
		}catch(err)
		{
			console.log(err);
			window.location.href = result.redirect_url;
		}
	} else {
		alert('Please enter a valid 6-digit code');
	}
}

// Add input validation to only allow numbers
document.getElementById('authCode').addEventListener('input', function(e) {
	this.value = this.value.replace(/[^0-9]/g, '');
});

// Export the function to make it globally accessible
window.validateCode = validateCode;

export { validateCode };

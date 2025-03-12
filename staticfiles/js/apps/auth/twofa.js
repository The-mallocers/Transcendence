import { navigateTo } from '../../spa/spa.js';

console.log("twoja loaded")

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
				const data = await response.json();
				localStorage.setItem('client_id', data.client_id);
				navigateTo(result.redirect); //make sure to change to redirect
			}
			// alert('Code submitted: ' + code);
		}catch(err)
		{
			console.log(err);
			navigateTo(result.redirect);
		}
	} else {
		alert('Please enter a valid 6-digit code');
	}
}

// Add input validation to only allow numbers
document.getElementById('authCode').addEventListener('input', function(e) {
	this.value = this.value.replace(/[^0-9]/g, '');
});

// Export the function to make it globally accessible, probably not the best practice, but it works
window.validateCode = validateCode;
export { validateCode };

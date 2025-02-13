const email = document.getElementById("data-email").getAttribute("email");

async function validateCode() {
	const code = document.getElementById('authCode').value;
	if(code.length === 6 && /^\d+$/.test(code)) {
		// Here you would typically send the code to your server for validation
		try{
			console.log(code);
			const response = await fetch("/auth/2facode", { // Remplace "/login" par l'URL de ton endpoint
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
				window.location.href = result.redirect_url;
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

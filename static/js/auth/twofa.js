//file to send a request to the server to enable or not 2fa

const toggleSwitch = document.getElementById('toggleSwitch');

// Method 2: Listen for changes
toggleSwitch.addEventListener('change', async function() {

	try
	{
		const response = await fetch("/api/auth/change_two_fa", { // Remplace "/login" par l'URL de ton endpoint
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				status : this.checked,
			}),
		});
		const result = await response.json();
		console.log(result);
	}catch(err)
	{
		console.log(err);
	}
});

// Method 3: If you want to programmatically change the state
function toggleOn() {
    toggleSwitch.checked = true;
}

function toggleOff() {
    toggleSwitch.checked = false;
}

// Method 4: Toggle the current state
function toggle() {
    toggleSwitch.checked = !toggleSwitch.checked;
}
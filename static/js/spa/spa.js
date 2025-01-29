async function handleRoute() {
    const path = window.location.pathname;
    const mainContent = document.querySelector('#app');
    
    switch(path) {
        case '/':
            const response = await fetch('/api/auth/login', {
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            const content = await response.json();
            mainContent.innerHTML = content.html;
            break;
    }
}


window.onload = async () => {
    console.log("coucou jvais executer ma fonction")
    await handleRoute(); 
};
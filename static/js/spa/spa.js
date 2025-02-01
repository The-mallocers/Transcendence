async function handleRoute() {
    const path = window.location.pathname;
    const mainContent = document.querySelector('#app');
    
    let response;
    let content;

    switch(path) {
        case '/':
            response = await fetch('/pages/auth/login', {
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            content = await response.json();
            mainContent.innerHTML = content.html;
            window.history.pushState({}, '', path);
            break;
        case '/api/auth/login':
            response = await fetch('/api/auth/login', {
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            content = await response.json();
            mainContent.innerHTML = content.html;
            window.history.pushState({}, '', path);
            break;


        default:
            response = `<div style="text-align: center; padding: 50px;">
                    <h1>404 - Page Not Found</h1>
                    <p>Sorry, the page you are looking for does not exist.</p>
                </div>`;
            mainContent.innerHTML = response
            window.history.pushState({}, '', path);
            break;

    }
}


window.onload = async () => {
    console.log("coucou jvais executer ma fonction")
    await handleRoute(); 
};
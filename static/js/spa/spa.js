// const app = document.getElementById('app');

// // Function to fetch data from the API
// async function fetchData(endpoint) {
//     const response = await fetch(`/api/${endpoint}`);
//     const data = await response.json();
//     return data;
// }

// // Function to render items
// function renderItems(items) {
//     app.innerHTML = items.map(item => `
//         <div>
//             <h2>${item.name}</h2>
//             <p>${item.description}</p>
//         </div>
//     `).join('');
// }

// // Function to handle routing
// function router() {
//     const path = window.location.hash.replace('#', '');
//     if (path === 'items') {
//         fetchData('items/').then(data => renderItems(data));
//     } else {
//         app.innerHTML = '<h1>Welcome to the SPA!</h1>';
//     }
// }

// // Event listener for hash change
// window.addEventListener('hashchange', router);

// // Initial load
// router();
console.log("SPA script loaded");

// class SPA {
//     constructor() {
//         this.mainContent = document.getElementById('app');
//         this.setupNavigation();
        
//         // Handle back/forward browser buttons
//         window.addEventListener('popstate', () => {
//             this.handleLocation();
//         });
        
//         // Handle initial page load
//         this.handleLocation();
//     }

//     setupNavigation() {
//         document.querySelectorAll('button[data-path]').forEach(button => {
//             button.addEventListener('click', (e) => {
//                 e.preventDefault();
//                 const path = e.target.getAttribute('data-path');
//                 console.log("path im trying to log is")
//                 console.log(path)
//                 if (path) {
//                     this.navigate(path);
//                 }
//             });
//         });
//     }
    

//     navigate(path) {
//         window.history.pushState({}, '', path);
//         this.handleLocation();
//     }

//     async handleLocation() {
//         const path = window.location.pathname;
//         try {
//             const content = await this.getContent(path);
//             this.updateContent(content);
//         } catch (error) {
//             console.error('Error loading content:', error);
//             //add the 404 error page here later.
//             // this.contentDiv.innerHTML = '<p>Error loading content</p>';
//         }
//     }

//     async getContent(path) {
//         // Add CSRF token to fetch request if needed
//         const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
//         const response = await fetch(path, {
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest',
//                 'X-CSRFToken': csrfToken,
//                 'Accept': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         return await response.json();
//     }

//     updateContent(data) {
//         if (typeof data === 'string') {
//             // If we got HTML directly, just update the content
//             this.mainContent.innerHTML = data;
//         } else {
//             // If we got a JSON object with title and content
//             if (data.title) {
//                 document.title = data.title;
//             }
//             if (data.content) {
//                 this.mainContent.innerHTML = data.content;
//             }
//         }
//     }
// }

// // Initialize the SPA when the DOM is loaded
// document.addEventListener('DOMContentLoaded', () => {
//     const spa = new SPA();
// });

class SPA {
    constructor() {
        this.setupNavigation();
        
        // Handle back/forward browser buttons
        window.addEventListener('popstate', () => this.handleLocation());
        
        // Handle initial page load
        this.handleLocation();
    }

    setupNavigation() {
        document.querySelectorAll('button[data-path]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const path = e.target.getAttribute('data-path');
                if (path) {
                    this.navigate(path);
                }
            });
        });
    }

    navigate(path) {
        window.history.pushState({}, '', path);
        this.handleLocation();
    }

    async handleLocation() {
        const path = window.location.pathname;
        try {
            const html = await this.getPage(path);
            this.updatePage(html);
        } catch (error) {
            console.error('Error loading page:', error);
        }
    }

    async getPage(path) {
        const response = await fetch(path, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        }); //Im adding the context thats its an xml request, im hoping to not have to use it, maybe well have to
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    updatePage(html) {
        // Replace the entire document's HTML
        console.log("updating page")
        document.open();
        document.write(html.html);
        document.close();
    }
}

// Initialize the SPA when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SPA();
});

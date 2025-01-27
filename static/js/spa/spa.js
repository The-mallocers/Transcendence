class SPA {
    constructor() {
        this.contentDiv = document.getElementById('content');
        this.setupNavigation();
        
        // Handle back/forward browser buttons
        window.addEventListener('popstate', () => {
            this.handleLocation();
        });
        
        // Handle initial page load
        this.handleLocation();
    }

    setupNavigation() {
        document.querySelectorAll('a, button[data-href]').forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                console.log("hi im js im proccing");
                const path = e.target.getAttribute('href') || e.target.getAttribute('data-href') || e.target.getAttribute('data-path');
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
            const content = await this.getContent(path);
            this.updateContent(content);
        } catch (error) {
            console.error('Error loading content:', error);
            this.contentDiv.innerHTML = '<p>Error loading content</p>';
        }
    }

    async getContent(path) {
        // Add CSRF token to fetch request if needed
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        const response = await fetch(path, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.text();
    }

    updateContent(content) {
        this.contentDiv.innerHTML = content;
    }
}

// Initialize the SPA when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const spa = new SPA();
});
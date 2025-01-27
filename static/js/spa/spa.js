class SPA {
    constructor() {
        this.mainContent = document.getElementById('app');
        this.setupNavigation();
        
        // Handle back/forward browser buttons
        window.addEventListener('popstate', () => {
            this.handleLocation();
        });
        
        // Handle initial page load
        this.handleLocation();
    }

    setupNavigation() {
        document.querySelectorAll('button[data-path]').forEach(button => {
            button.addEventListener('click', (e) => {
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
            const content = await this.getContent(path);
            this.updateContent(content);
        } catch (error) {
            console.error('Error loading content:', error);
            //add the 404 error page here later.
            // this.contentDiv.innerHTML = '<p>Error loading content</p>';
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
        // Update the title if provided
        if (content.title) {
            document.title = content.title;
        }

        // Update the main content
        if (content.content) {
            this.mainContent.innerHTML = content.content;
        }
    }
}

// Initialize the SPA when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const spa = new SPA();
});
FROM nginx:latest

# Remove default nginx configuration
RUN rm /etc/nginx/nginx.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Set permissions
RUN chmod 644 /etc/nginx/nginx.conf

# Expose port
EXPOSE 80 443
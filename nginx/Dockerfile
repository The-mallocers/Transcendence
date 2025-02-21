FROM debian:bullseye

RUN apt-get update && \
    apt-get install -y nginx openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/nginx/certs && \
    chmod 700 /etc/nginx/certs &&\
    openssl req -x509 -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/certs/key.pem \
    -out /etc/nginx/certs/cert.pem \
    -subj "/CN=localhost"

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]

# FROM nginx:latest

# RUN mkdir -p /etc/nginx/certs && \
#     chmod 700 /etc/nginx/certs

# # Remove default nginx configuration
# RUN rm /etc/nginx/nginx.conf

# # Copy custom nginx configuration
# COPY nginx.conf /etc/nginx/nginx.conf

# # Set permissions
# RUN chmod 644 /etc/nginx/nginx.conf

# RUN mkdir -p /etc/nginx/certs && \
#     chmod 700 /etc/nginx/certs

# # Generate self-signed certificate for localhost
# RUN openssl req -x509 -nodes \
#     -days 365 \
#     -newkey rsa:2048 \
#     -keyout /etc/nginx/certs/key.pem \
#     -out /etc/nginx/certs/cert.pem \
#     -subj "/CN=localhost"

# Expose port
# EXPOSE 80 443

# # CMD ["nginx", "-g", "daemon off;"]
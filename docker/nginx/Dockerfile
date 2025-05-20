FROM debian:bullseye

RUN apt-get update && \
    apt-get install -y nginx openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy custom nginx configuration

COPY nginx.conf /etc/nginx/nginx.conf
#COPY nginx.conf /etc/nginx/templates/default.conf.template

#create full host name
CMD ["sh", "-c", "envsubst < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf"]

CMD ["nginx", "-g", "daemon off;"]
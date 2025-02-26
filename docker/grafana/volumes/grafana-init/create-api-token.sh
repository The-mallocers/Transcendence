#!/bin/bash
set -e

# Wait for Grafana to start
echo "Waiting for Grafana to start..."
until $(curl --output /dev/null --silent --fail http://localhost:3000/api/health); do
  printf '.'
  sleep 2
done
echo "Grafana is up and running!"

# Create API token (expires in 1 year = 8760h)
TOKEN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"name":"auto-token", "role": "Admin", "secondsToLive": 31536000}' http://admin:${GF_SECURITY_ADMIN_PASSWORD}@localhost:3000/api/auth/keys)

# Extract token
API_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"key":"[^"]*' | grep -o '[^"]*$')

# Save token to file
echo "API_TOKEN=$API_TOKEN" > /grafana-init/token.env
echo "Token generated and saved to /grafana-init/token.env"

# Save token to a location your application can access
echo $API_TOKEN > /var/lib/grafana/token.txt
chmod 644 /var/lib/grafana/token.txt
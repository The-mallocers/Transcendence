#!/bin/bash

set -e

# Define the secret folder path
SECRET_FOLDER="./secrets"
VENV_FOLDER="./.venv" # Temporary virtual environment folder

# Define color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check OS for sed compatibility
SED_INPLACE() {
  # Usage: SED_INPLACE <expression> <file>
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "$1" "$2"
  else
    sed -i "$1" "$2"
  fi
}

# Create a virtual environment (Linux: ensure python-venv is installed)
create_venv() {
  if ! python3 -m venv --help > /dev/null 2>&1; then
    echo -e "${RED}Error: python-venv is not installed.${NC}"
    if [[ "$(uname)" == "Darwin" ]]; then
      echo -e "${YELLOW}Install Python 3 from Homebrew or official installer, which includes venv.${NC}"
    else
      echo -e "${YELLOW}On Debian/Ubuntu, run: sudo apt install python-venv${NC}"
    fi
    exit 1
  fi

  python3 -m venv "$VENV_FOLDER"
  # shellcheck disable=SC1091
  source "$VENV_FOLDER/bin/activate"
  export PIP_DISABLE_PIP_VERSION_CHECK=1
  pip install --quiet django
}

# Destroy the virtual environment
destroy_venv() {
  # deactivate only if venv is active
  if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
  fi
  rm -rf "$VENV_FOLDER"
}

# Generate a Django SECRET_KEY using the virtual environment
generate_django_secret_key() {
  # shellcheck disable=SC1091
  source "$VENV_FOLDER/bin/activate"
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# Generate a JWT SECRET_KEY using the virtual environment
generate_jwt_secret_key() {
  # shellcheck disable=SC1091
  source "$VENV_FOLDER/bin/activate"
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# Generate a base32 SECRET_FA_KEY using the virtual environment
generate_secret_fa_key() {
  # shellcheck disable=SC1091
  source "$VENV_FOLDER/bin/activate"
  python3 -c "import secrets, base64; random_bytes = secrets.token_bytes(20); print(base64.b32encode(random_bytes).decode('utf-8').rstrip('='))"
}

# Get the hostname
get_hostname() {
  hostname
}

# Create cert.pem and key.pem files if missing
generate_pem_files() {
  local cert_path="$SECRET_FOLDER/cert.pem"
  local key_path="$SECRET_FOLDER/key.pem"

  mkdir -p "$SECRET_FOLDER"
  if [ ! -f "$cert_path" ]; then
    echo -e "${YELLOW}Creating $cert_path...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$key_path" -out "$cert_path" -subj "/CN=localhost"
  fi

  if [ ! -f "$key_path" ]; then
    echo -e "${YELLOW}Creating $key_path...${NC}"
    openssl genrsa -out "$key_path" 2048
  fi
}

# Check if 42_client and 42_secret exist
check_42_files() {
  local client_file="$SECRET_FOLDER/42_client"
  local secret_file="$SECRET_FOLDER/42_secret"

  if [ ! -f "$client_file" ] || [ ! -f "$secret_file" ]; then
    echo -e "${RED}Error: Missing required files in $SECRET_FOLDER directory:${NC}"
    if [ ! -f "$client_file" ]; then echo -e "${RED}  - 42_client${NC}"; fi
    if [ ! -f "$secret_file" ]; then echo -e "${RED}  - 42_secret${NC}"; fi
    echo -e "${YELLOW}You can create files with this command: make secrets${NC}"
    destroy_venv
    exit 1
  fi
}

# Generate .env if missing
generate_env_file() {
  if [ -f .env ]; then
    echo -e "${CYAN}Environment file already exists. Updating required fields...${NC}"

    # Update DJANGO_HOSTNAME with cross-platform sed
    if grep -q "^DJANGO_HOSTNAME=" .env; then
      SED_INPLACE "s/^DJANGO_HOSTNAME=.*/DJANGO_HOSTNAME=$(get_hostname)/" .env
    else
      echo "DJANGO_HOSTNAME=$(get_hostname)" >> .env
    fi
    echo -e "${GREEN}DJANGO_HOSTNAME has been updated in the existing environment file.${NC}"
  else
    echo -e "${BLUE}Creating a new environment file with dynamic values...${NC}"
    cat <<EOL > .env
# ══ Secrets ═════════════════════════════════════════════════════════════════════════ #
# Keys
DJANGO_SECRET_KEY='$(generate_django_secret_key)'
JWT_SECRET_KEY='$(generate_jwt_secret_key)'
SECRET_FA_KEY='$(generate_secret_fa_key)'
AUTH_42_CLIENT='$(cat $SECRET_FOLDER/42_client)'
AUTH_42_SECRET='$(cat $SECRET_FOLDER/42_secret)'

# Password
DATABASE_PASSWORD='admin'
GRAFANA_PASSWORD='admin'
ADMIN_PWD='123456789!'

# ══ Variables ═══════════════════════════════════════════════════════════════════════ #
# SSL
SSL_CERT_PATH=$SECRET_FOLDER/cert.pem
SSL_KEY_PATH=$SECRET_FOLDER/key.pem

# Database PostgreSQL
DATABASE_NAME='dockerdjango'
DATABASE_USERNAME='postgres'
DATABASE_HOST='db'
DATABASE_PORT='5432'

# JWT
JWT_EXP_ACCESS_TOKEN='30' # In minutes
JWT_EXP_REFRESH_TOKEN='7' # In days

# Admin client
ADMIN_EMAIL='admin@transcendence.fr'
ADMIN_USERNAME='admin'

DJANGO_HOSTNAME='$(get_hostname)'
EOL
    echo -e "${GREEN}Environment file has been created with dynamic values.${NC}"
  fi
}

# Main execution
create_venv
check_42_files
generate_pem_files
generate_env_file
destroy_venv
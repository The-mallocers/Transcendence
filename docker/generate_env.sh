#!/bin/bash

set -e

SECRET_FOLDER="./secrets"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Cross-platform sed -i compatibility
SED_INPLACE() {
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "$1" "$2"
  else
    sed -i "$1" "$2"
  fi
}

# Generate keys
generate_django_secret_key() { python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"; }
generate_jwt_secret_key()    { python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"; }
generate_secret_fa_key()     { python3 -c "import secrets, base64; random_bytes = secrets.token_bytes(20); print(base64.b32encode(random_bytes).decode('utf-8').rstrip('='))"; }
get_hostname()               { hostname; }

# Early check for secrets folder and required files
check_secrets_accessible() {
  if [ ! -d "$SECRET_FOLDER" ] || [ ! -r "$SECRET_FOLDER" ]; then
    echo -e "${RED}Error: '$SECRET_FOLDER' directory does not exist or is not readable.${NC}"
    exit 1
  fi

  local files=("42_client" "42_secret")
  local missing=0
  for f in "${files[@]}"; do
    local path="$SECRET_FOLDER/$f"
    if [ ! -f "$path" ] || [ ! -r "$path" ]; then
      echo -e "${RED}Error: $f is missing or not readable in $SECRET_FOLDER.${NC}"
      missing=1
    fi
  done

  if [ "$missing" -eq 1 ]; then
    echo -e "${YELLOW}You can create missing files with: make secrets${NC}"
    exit 1
  fi
}

# Remove ALL whitespace from 42_secret and 42_client
trim_42_files_whitespace() {
  local files=("$SECRET_FOLDER/42_secret" "$SECRET_FOLDER/42_client")
  for file in "${files[@]}"; do
    if [ -f "$file" ]; then
      tr -d '[:space:]' < "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    fi
  done
}

# Generate cert.pem and key.pem if not present
generate_pem_files() {
  local cert_path="$SECRET_FOLDER/cert.pem" key_path="$SECRET_FOLDER/key.pem"
  mkdir -p "$SECRET_FOLDER"
  if [ ! -f "$cert_path" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$key_path" -out "$cert_path" -subj "/CN=localhost" >/dev/null 2>&1
  fi
  if [ ! -f "$key_path" ]; then
    openssl genrsa -out "$key_path" 2048 >/dev/null 2>&1
  fi
}

# Check for default passwords and warn user
warn_if_default_passwords() {
  local warn=0 val
  for var in ADMIN_PWD DATABASE_PASSWORD GRAFANA_PASSWORD; do
    val=$(grep "^${var}=" .env | head -n1 | cut -d= -f2- | tr -d "'\"" || true)
    if [[ "$var" == "ADMIN_PWD" && "$val" == "123456789!" ]]; then
      echo -e "${RED}Warning: ADMIN_PWD is set to the default value!${NC}"
      warn=1
    elif [[ "$val" == "admin" ]]; then
      echo -e "${RED}Warning: $var is set to the default value!${NC}"
      warn=1
    fi
  done
  if [ "$warn" = 1 ]; then
    echo -e "${YELLOW}It is strongly recommended to change these passwords in your .env file.\nRun 'make password' to change password.${NC}"
  fi
  return 0
}

validate_admin_password() {
  local pwd="$1"
  if [[ ${#pwd} -lt 8 ]]; then
    echo -e "${RED}Error: ADMIN_PWD must be at least 8 characters long.${NC}"
    exit 1
  fi
  if ! [[ "$pwd" =~ [^a-zA-Z0-9] ]]; then
    echo -e "${RED}Error: ADMIN_PWD must contain at least one special character.${NC}"
    exit 1
  fi
  if ! [[ "$pwd" =~ [0-9] ]]; then
    echo -e "${RED}Error: ADMIN_PWD must contain at least one digit.${NC}"
    exit 1
  fi
}

# Prompt for passwords
prompt_password() {
  local varname="$1"
  local prompt_text="$2"
  local default_pwd="$3"
  local result
  if [ -t 0 ]; then
    read -r -p "$prompt_text (default: ${default_pwd}): " result
    result="${result:-$default_pwd}"
  else
    result="$default_pwd"
  fi
  echo "$result"
}

generate_env_file() {
  local admin_pwd db_pwd grafana_pwd
  pip install django > /dev/null 2>&1
  if [ -f .env ]; then

    local current_hostname
    current_hostname=$(grep "^DJANGO_HOSTNAME=" .env | cut -d'=' -f2- | tr -d "'\"")
    local new_hostname
    new_hostname=$(get_hostname)

    if [ -z "$current_hostname" ]; then
      echo "DJANGO_HOSTNAME=$new_hostname" >> .env
      echo -e "${GREEN}DJANGO_HOSTNAME has been added to the environment file.${NC}"
    elif [ "$current_hostname" != "$new_hostname" ]; then
      SED_INPLACE "s/^DJANGO_HOSTNAME=.*/DJANGO_HOSTNAME=$new_hostname/" .env
      echo -e "${GREEN}DJANGO_HOSTNAME has been updated in the environment file.${NC}"
    fi
    admin_pwd=$(grep "^ADMIN_PWD=" .env | head -n1 | cut -d= -f2- | tr -d "'\"" || true)
    validate_admin_password "$admin_pwd"
    warn_if_default_passwords
  else
    admin_pwd=$(prompt_password "ADMIN_PWD" "Set ADMIN_PWD" "123456789!")
    db_pwd=$(prompt_password "DATABASE_PASSWORD" "Set DATABASE_PASSWORD" "admin")
    grafana_pwd=$(prompt_password "GRAFANA_PASSWORD" "Set GRAFANA_PASSWORD" "admin")
    cat <<EOL > .env
# ══ Secrets ═════════════════════════════════════════════════════════════════════════ #
DJANGO_SECRET_KEY='$(generate_django_secret_key)'
JWT_SECRET_KEY='$(generate_jwt_secret_key)'
SECRET_FA_KEY='$(generate_secret_fa_key)'

# Password
DATABASE_PASSWORD='${db_pwd}'
GRAFANA_PASSWORD='${grafana_pwd}'
ADMIN_PWD='${admin_pwd}'

# ══ Variables ═══════════════════════════════════════════════════════════════════════ #
SSL_CERT_PATH=$SECRET_FOLDER/cert.pem
SSL_KEY_PATH=$SECRET_FOLDER/key.pem

S_42_AUTH_PATH=./secrets/42_secret
U_42_AUTH_PATH=./secrets/42_client

DATABASE_NAME='dockerdjango'
DATABASE_USERNAME='postgres'
DATABASE_HOST='db'
DATABASE_PORT='5432'

JWT_EXP_ACCESS_TOKEN='30' # In minutes
JWT_EXP_REFRESH_TOKEN='7' # In days

ADMIN_EMAIL='admin@transcendence.fr'
ADMIN_USERNAME='admin'

DJANGO_HOSTNAME='$(get_hostname)'
EOL
    warn_if_default_passwords
    echo -e "${GREEN}Environment file has been created with dynamic values.${NC}"
  fi
}

# --- Main script execution order ---

check_secrets_accessible
trim_42_files_whitespace
generate_pem_files
generate_env_file
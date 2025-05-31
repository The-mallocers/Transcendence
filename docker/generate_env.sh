#!/bin/bash

# Don't use set -e as we want to handle errors gracefully
# Instead, we'll check return codes and handle errors explicitly

SECRET_FOLDER="./secrets"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Error handling function
error_exit() {
  echo -e "${RED}ERROR: $1${NC}" >&2
  exit 1
}

error_msg() {
  echo -e "${RED}ERROR: $1${NC}" >&2
}

# Success message function
success_msg() {
  echo -e "${GREEN}$1${NC}"
}

# Warning message function
warning_msg() {
  echo -e "${YELLOW}$1${NC}"
}

# Info message function
info_msg() {
  echo -e "${CYAN}$1${NC}"
}

# Cross-platform sed -i compatibility
SED_INPLACE() {
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "$1" "$2"
  else
    sed -i "$1" "$2"
  fi
}

# Generate keys with fallbacks
generate_django_secret_key() {
  local key
  # Try using Django's get_random_secret_key
  key=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null) && echo "$key" && return
  # Fallback to a custom implementation if Django is not available
  key=$(python -c "import random, string; print(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for i in range(50)))" 2>/dev/null) && echo "$key" && return
  # Final fallback using /dev/urandom
  key=$(LC_ALL=C tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50) && echo "$key" && return
  # If all methods fail
  error_exit "Failed to generate Django secret key"
}

generate_jwt_secret_key() {
  local key
  # Try using Django's get_random_secret_key
  key=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null) && echo "$key" && return
  # Fallback to a custom implementation if Django is not available
  key=$(python -c "import random, string; print(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for i in range(50)))" 2>/dev/null) && echo "$key" && return
  # Final fallback using /dev/urandom
  key=$(LC_ALL=C tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50) && echo "$key" && return
  # If all methods fail
  error_exit "Failed to generate JWT secret key"
}

generate_secret_fa_key() {
  local key
  # Try using Python's secrets module
  key=$(python -c "import secrets, base64; random_bytes = secrets.token_bytes(20); print(base64.b32encode(random_bytes).decode('utf-8').rstrip('='))" 2>/dev/null) && echo "$key" && return
  # Fallback if Python's secrets module is not available
  key=$(python -c "import os, base64; random_bytes = os.urandom(20); print(base64.b32encode(random_bytes).decode('utf-8').rstrip('='))" 2>/dev/null) && echo "$key" && return
  # Final fallback using /dev/urandom and base32 encoding
  key=$(head -c 20 /dev/urandom | base64 | tr -d '=+/' | tr -d '\n' | head -c 32) && echo "$key" && return
  # If all methods fail
  error_exit "Failed to generate 2FA secret key"
}

get_hostname() {
  local host
  host=$(hostname 2>/dev/null) && echo "$host" && return
  echo "localhost" # Fallback to localhost if hostname command fails
}

# Create secrets directory and files if they don't exist
create_secrets_files() {
  # Create secrets directory with secure permissions if it doesn't exist
  if [ ! -d "$SECRET_FOLDER" ]; then
    if ! mkdir -m 700 -p "$SECRET_FOLDER"; then
      error_exit "Failed to create $SECRET_FOLDER directory with secure permissions."
    fi
  fi

  # Check folder permissions and fix if necessary
  if [ ! -r "$SECRET_FOLDER" ] || [ ! -w "$SECRET_FOLDER" ] || [ ! -x "$SECRET_FOLDER" ]; then
    if [ "$(perm_check $SECRET_FOLDER)" != "700" ]; then
      if ! chmod 700 "$SECRET_FOLDER"; then
        error_exit "Failed to set secure permissions on $SECRET_FOLDER directory."
      fi
      info_msg "Fixing permission on $SECRET_FOLDER."
    fi
  fi

  # Create 42_client file if it doesn't exist
  if [ ! -f "$SECRET_FOLDER/42_client" ]; then
    echo -e "${CYAN}Enter the key for 42_client:${NC} \c"
    read client_key
    client_key=$(echo "$client_key" | tr -d '\r' | xargs)
    if [ -z "$client_key" ]; then
      error_exit "Error: 42_client key cannot be empty."
    fi
    if ! printf "%s" "$client_key" > "$SECRET_FOLDER/42_client"; then
      error_exit "Failed to write to $SECRET_FOLDER/42_client file."
    fi
  fi
  if [ "$(perm_check "$SECRET_FOLDER/42_client")" != "644" ]; then
    if ! chmod 644 "$SECRET_FOLDER/42_client"; then
      warning_msg "Warning: Failed to set secure permissions on 42_client file."
    fi
    info_msg "Fixing permission on 42_client."
  fi

  # Create 42_secret file if it doesn't exist
  if [ ! -f "$SECRET_FOLDER/42_secret" ]; then
    echo -e "${CYAN}Enter the key for 42_secret:${NC} \c"
    read secret_key
    secret_key=$(echo "$secret_key" | tr -d '\r' | xargs)
    if [ -z "$secret_key" ]; then
      error_exit "Error: 42_secret key cannot be empty."
    fi
    if ! printf "%s" "$secret_key" > "$SECRET_FOLDER/42_secret"; then
      error_exit "Failed to write to $SECRET_FOLDER/42_secret file."
    fi
  fi
  if [ "$(perm_check "$SECRET_FOLDER/42_secret")" != "644" ]; then
    if ! chmod 644 "$SECRET_FOLDER/42_secret"; then
      warning_msg "Warning: Failed to set secure permissions on 42_secret file."
    fi
    info_msg "Fixing permission on 42_secret."
  fi
}

# Remove ALL whitespace from 42_secret and 42_client
trim_42_files_whitespace() {
  local files=("$SECRET_FOLDER/42_secret" "$SECRET_FOLDER/42_client")
  for file in "${files[@]}"; do
    if [ -f "$file" ] && [ -r "$file" ] && [ -w "$file" ]; then
      if ! tr -d '[:space:]' < "$file" > "${file}.tmp"; then
        error_exit "Failed to process $file - could not remove whitespace"
      fi

      if ! mv "${file}.tmp" "$file"; then
        rm -f "${file}.tmp" 2>/dev/null # Clean up temp file
        error_exit "Failed to update $file after processing"
      fi
    elif [ -f "$file" ]; then
      error_exit "File $file exists but has incorrect permissions"
    fi
  done
}

# Generate cert.pem and key.pem if not present
generate_pem_files() {
  local cert_path="$SECRET_FOLDER/cert.pem" key_path="$SECRET_FOLDER/key.pem"

  if [ ! -f "$cert_path" ] || [ ! -f "$key_path" ]; then
    if ! openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$key_path" -out "$cert_path" -subj "/CN=$(get_hostname)" >/dev/null 2>&1;
    then
      error_exit "Failed to generate SSL certificate and key"
    fi
    info_msg "Cert.pem file was successfully created."
    info_msg "Key.pem file was successfully created."
  else
    if [ ! -f "$cert_path" ]; then
      # (unlikely if key.pem exists, but just in case)
      # Generate only cert, using existing key
      if ! openssl req -x509 -nodes -days 365 -key "$key_path" -out "$cert_path" -subj "/CN=$(get_hostname)" >/dev/null 2>&1; then
        error_exit "Failed to generate SSL certificate"
      fi
      info_msg "Cert.pem file was successfully created."
    fi
    if [ ! -f "$key_path" ]; then
      if ! openssl genrsa -out "$key_path" 2048 >/dev/null 2>&1; then
        error_exit "Failed to generate SSL key"
      fi
      info_msg "Key.pem file was successfully created."
    fi
  fi
}

# Check for default passwords and warn user
warn_if_default_passwords() {
  # Check if .env file exists and is readable
  if [ ! -f ".env" ] || [ ! -r ".env" ]; then
    return 1
  fi

  for var in ADMIN_PWD DATABASE_PASSWORD GRAFANA_PASSWORD; do
    val=$(grep "^${var}=" .env | head -n1 | cut -d= -f2- | tr -d "'\"" || true)

    # Skip if variable not found
    if [ -z "$val" ]; then
      continue
    fi

    if [[ "$var" == "ADMIN_PWD" && "$val" == "123456789!" ]]; then
      return 2  # Default found!
    elif [[ "$val" == "admin" ]]; then
      return 2  # Default found!
    fi
  done

  return 0  # No defaults found
}

validate_admin_password() {
  local pwd="$1"

  # Check if password is empty
  if [ -z "$pwd" ]; then
    error_exit "ADMIN_PWD cannot be empty"
  fi

  # Check password length
  if [[ ${#pwd} -lt 8 ]]; then
    error_exit "ADMIN_PWD must be at least 8 characters long"
  fi

  # Check for special character
  if ! [[ "$pwd" =~ [^a-zA-Z0-9] ]]; then
    error_exit "ADMIN_PWD must contain at least one special character"
  fi

  # Check for digit
  if ! [[ "$pwd" =~ [0-9] ]]; then
    error_exit "ADMIN_PWD must contain at least one digit"
  fi

  # Password is valid
  return 0
}

# Prompt for passwords with improved user interaction
prompt_password() {
  local varname="$1"
  local prompt_text="$2"
  local default_pwd="$3"
  local result

  # Use colored prompt for better visibility
  echo -e "${CYAN}$prompt_text${NC} (default: ${default_pwd}): \c"
  # Read user input without timeout
  read -r result || {
    echo "Using default value due to non-interactive environment." >&2
    result="$default_pwd"
  }
  result="${result:-$default_pwd}"

  # For ADMIN_PWD, validate the password
  if [[ "$varname" == "ADMIN_PWD" ]]; then
    # Validate the password
    if [[ ${#result} -lt 8 ]]; then
      error_exit "Password must be at least 8 characters long."
    elif ! [[ "$result" =~ [^a-zA-Z0-9] ]]; then
      error_exit "Password must contain at least one special character."
    elif ! [[ "$result" =~ [0-9] ]]; then
      error_exit "Password must contain at least one digit."
    fi
  fi

  PROMPT_PASSWORD_RESULT="$result"
}

# Validate existing .env file to ensure all required variables are present
validate_env_file() {
  local env_file="$1"
  local missing=0

  # List of required variables
  local required_vars=(
    "DJANGO_SECRET_KEY"
    "JWT_SECRET_KEY"
    "SECRET_FA_KEY"
    "DATABASE_PASSWORD"
    "GRAFANA_PASSWORD"
    "ADMIN_PWD"
    "SSL_CERT_PATH"
    "SSL_KEY_PATH"
    "S_42_AUTH_PATH"
    "U_42_AUTH_PATH"
    "DATABASE_NAME"
    "DATABASE_USERNAME"
    "DATABASE_HOST"
    "DATABASE_PORT"
    "JWT_EXP_ACCESS_TOKEN"
    "JWT_EXP_REFRESH_TOKEN"
    "ADMIN_EMAIL"
    "ADMIN_USERNAME"
    "DJANGO_HOSTNAME"
  )

    if [ ! -r .env ]; then
      error_exit "Environement file can't be read or you don't have the permission."
    fi

  # Check each required variable
  for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" "$env_file"; then
      warning_msg "Required variable $var is missing in $env_file"
      missing=1
    fi
  done

  if [[ "$missing" -gt 0 ]]; then
    error_exit "You can't run with missing variable. Please run 'make reenv'"
  fi

  return $missing
}

# Portable permission checker for GNU and BSD stat
perm_check() {
  if stat --version >/dev/null 2>&1; then
    stat -c '%a' "$1"
  else
    stat -f '%Lp' "$1"
  fi
}

check_and_fix_permissions() {
  local files=(".env" "$SECRET_FOLDER/42_secret" "$SECRET_FOLDER/42_client" \
    "$SECRET_FOLDER/key.pem" "$SECRET_FOLDER/cert.pem")
  local dir="$SECRET_FOLDER"

  # Check and fix directory permissions
  if [ -d "$dir" ]; then
    if [ "$(perm_check "$dir")" != "700" ]; then
      info_msg "Fixing permissions on $dir"
      if ! chmod 700 "$dir"; then
        error_exit "Failed to set permissions 700 on $dir"
      fi
    fi
  else
    error_exit "Directory $dir does not exist"
  fi

  # Check and fix file permissions
  for file in "${files[@]}"; do
    if [ -f "$file" ]; then
      if [ "$file" == "$SECRET_FOLDER/key.pem" ]; then
        if [ "$(perm_check "$file")" != "600" ]; then
          info_msg "Fixing permissions on key.pem files..."
          if ! chmod 600 "$file"; then
            error_exit "Failed to set permissions 600 on $file"
          fi
        fi
      elif [ "$(perm_check "$file")" != "644" ]; then
        info_msg "Fixing permissions on $file"
        if ! chmod 644 "$file"; then
          error_exit "Failed to set permissions 644 on $file"
        fi
      fi
    fi
  done
}

generate_env_file() {
  local admin_pwd db_pwd grafana_pwd

  # Try to install Django for secret key generation, but don't fail if it doesn't work
  if command -v pip >/dev/null 2>&1; then
    pip install django >/dev/null 2>&1
  fi

  if [ -f .env ] && [ -s .env ]; then #if .env exist
    # Validate existing .env file
    validate_env_file ".env"


    # Update hostname if needed
    local current_hostname
    current_hostname=$(grep "^DJANGO_HOSTNAME=" .env | cut -d'=' -f2- | tr -d "'\"" 2>/dev/null || echo "")
    local new_hostname
    new_hostname=$(get_hostname)

    if [ -z "$current_hostname" ]; then
      echo "DJANGO_HOSTNAME=$new_hostname" >> .env
    elif [ "$current_hostname" != "$new_hostname" ]; then
      SED_INPLACE "s/^DJANGO_HOSTNAME=.*/DJANGO_HOSTNAME=$new_hostname/" .env
    fi

    # Validate admin password
    admin_pwd=$(grep "^ADMIN_PWD=" .env | head -n1 | cut -d= -f2- | tr -d "'\"" 2>/dev/null || echo "")
    if [ -z "$admin_pwd" ]; then
      prompt_password "ADMIN_PWD" "Set ADMIN_PWD" "123456789!"
      admin_pwd="$PROMPT_PASSWORD_RESULT"
      echo "ADMIN_PWD='$admin_pwd'" >> .env
    else
      # Validate the existing admin password
      if ! validate_admin_password "$admin_pwd" 2>/dev/null; then
        prompt_password "ADMIN_PWD" "Set a new ADMIN_PWD" "123456789!"
        admin_pwd="$PROMPT_PASSWORD_RESULT"
        SED_INPLACE "s/^ADMIN_PWD=.*/ADMIN_PWD='$admin_pwd'/" .env
      fi
    fi

    # Check for default passwords
    if ! warn_if_default_passwords; then
      error_msg "Default passwords detected. Run 'make passwords' to change them."
    fi

  else
    prompt_password "ADMIN_PWD" "Set ADMIN_PWD" "123456789!"
    admin_pwd="$PROMPT_PASSWORD_RESULT"
    prompt_password "DATABASE_PASSWORD" "Set DATABASE_PASSWORD" "admin"
    db_pwd="$PROMPT_PASSWORD_RESULT"
    prompt_password "GRAFANA_PASSWORD" "Set GRAFANA_PASSWORD" "admin"
    grafana_pwd="$PROMPT_PASSWORD_RESULT"

    # Generate the .env file
    cat <<EOL > .env || error_exit "Failed to create .env file"
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

    # Set proper permissions for .env file
    chmod 644 .env

    # Check for default passwords
    if ! warn_if_default_passwords; then
      error_msg "Default passwords detected. Run 'make passwords' to change them."
    fi
  fi
}

# Function to check if required commands are available
check_required_commands() {
  local missing=0
  local commands=("python" "openssl" "grep" "sed" "tr")

  for cmd in "${commands[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      error_exit "Required command '$cmd' is not available. Please install it and try again."
      missing=1
    fi
  done

  return $missing
}

# Main function to orchestrate the script execution
main() {
  # Check for required commands
  check_required_commands

  # Execute the main functions in order, with error handling
  create_secrets_files

  if ! trim_42_files_whitespace; then
    error_exit "Failed to process 42 authentication files"
  fi

  if ! generate_pem_files; then
    error_exit "Failed to generate SSL certificate files"
  fi

  if ! generate_env_file; then
    error_exit "Failed to generate or update .env file"
  fi

  check_and_fix_permissions
}

# --- Main script execution ---
# Trap for cleanup on exit
trap 'echo -e "${RED}Script execution interrupted.${NC}"; exit 1' INT TERM

# Run the main function
main "$@"

# Exit with success
exit 0

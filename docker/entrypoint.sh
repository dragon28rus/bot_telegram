#!/usr/bin/env sh
set -e

if [ "${RUN_PASSWORD_MIGRATION_ON_START}" = "true" ]; then
  echo "Running password migration..."
  python scripts/migrate_encrypt_passwords.py
fi

echo "Starting bot..."
exec python main.py

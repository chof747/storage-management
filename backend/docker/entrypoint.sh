#!/usr/bin/env sh
set -e

log() {
  # Timestamp + log level + message
  echo "$(date '+%Y-%m-%d %H:%M:%S') [entrypoint] $*"
}

log "Starting database migration…"
if pdm run migrate; then
  log "Database migration completed successfully."
else
  log "Database migration FAILED!"
  exit 1
fi

log "Starting application server…"
exec pdm run serve
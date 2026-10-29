#!/usr/bin/env bash
# Archives the app log and takes a PostgreSQL backup.
# Scheduled every 2 minutes from cron (see README):
#   */2 * * * * /opt/myapp/cron-job.sh >> /opt/myapp/logs/cron.log 2>&1
set -euo pipefail

# cron runs with a minimal PATH, so make sure docker can be found
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

cd "$(dirname "$0")"

KEEP=30
TS=$(date +%Y%m%d_%H%M%S)

mkdir -p log_archive backups

# 1. Copy the current log file into the archive
if [ -f logs/app.log ]; then
    cp logs/app.log "log_archive/app_${TS}.log"
    echo "[$TS] Archived logs/app.log -> log_archive/app_${TS}.log"
else
    echo "[$TS] logs/app.log not found, skipping log archive"
fi

# 2. Dump the database from inside the db container (uses the container's own env)
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
    | gzip > "backups/db_${TS}.sql.gz"
echo "[$TS] Database backup saved to backups/db_${TS}.sql.gz"

# 3. Keep only the newest $KEEP files in each folder so the disk doesn't fill up
for dir in log_archive backups; do
    ls -1t "$dir" | grep -v '^\.gitkeep$' | tail -n +$((KEEP + 1)) | while read -r old; do
        rm -f "$dir/$old"
    done
done

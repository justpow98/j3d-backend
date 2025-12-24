#!/bin/bash
set -e

echo "=== J3D Backend Container Startup ==="

# Wait for database to be ready (if using postgres)
if [[ "$DATABASE_URL" == postgresql* ]] || [[ "$DATABASE_URL" == postgres* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_PORT=${DB_PORT:-5432}
    
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    
    echo "PostgreSQL is ready!"
fi

# Run migrations or create tables
if [ "$RUN_DB_UPGRADE" = "1" ] || [ "$AUTO_MIGRATE" = "1" ]; then
    echo "Running database migrations..."
    python scripts/migrate_db.py --config "${FLASK_CONFIG:-production}" --apply || {
        echo "Migration failed, trying to generate first..."
        python scripts/migrate_db.py --config "${FLASK_CONFIG:-production}" -m "Initial schema" --apply
    }
elif [ "$AUTO_DB_CREATE" = "1" ]; then
    echo "Creating database tables..."
    python scripts/init_db.py --config "${FLASK_CONFIG:-production}"
else
    echo "Skipping automatic database setup (set AUTO_MIGRATE=1 or AUTO_DB_CREATE=1 to enable)"
fi

echo "Starting Flask application..."
exec "$@"

# Database Setup & Management

Guide for database setup, configuration, and management.

## Overview

The application uses SQLAlchemy ORM with support for:
- **Development**: SQLite (in-process, file-based)
- **Production**: PostgreSQL (recommended)

## Database Configuration

### Environment Variables

Set in `.env` file:

```bash
# Database URL format
DATABASE_URL=postgresql://user:password@localhost:5432/j3d_db

# PostgreSQL specific
DB_HOST=localhost
DB_PORT=5432
DB_NAME=j3d_db
DB_USER=j3d_user
DB_PASSWORD=secure_password

# Connection pooling
DB_POOL_SIZE=10
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
```

### Connection Strings

**PostgreSQL (Production):**
```
postgresql://username:password@hostname:5432/database_name
```

**SQLite (Development):**
```
sqlite:///instance/app.db
```

**SQLite (Testing):**
```
sqlite:///:memory:
```

## SQLite Setup (Development)

SQLite is perfect for local development.

### Features
- No installation needed
- File-based (instance/app.db)
- Good for testing
- Auto-migrations on startup

### Automatic Setup

Database auto-initializes on startup:

```bash
python app.py
```

The `init_db()` function:
1. Creates `instance/` directory if missing
2. Creates database file if missing
3. Creates all tables from models
4. Returns success message

### Manual Setup

If needed:

```python
from app import app, db

with app.app_context():
    db.create_all()
    print("Database initialized")
```

### Database File Location

```
j3d-backend/
├── instance/
│   └── app.db          ← SQLite database file
├── app.py
├── models.py
└── ...
```

### Resetting Database

For testing, reset the database:

```python
from app import app, db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset")
```

## PostgreSQL Setup (Production)

PostgreSQL is required for production deployments.

### Installation

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
1. Download from https://www.postgresql.org/download/windows/
2. Run installer
3. Choose default options
4. Remember superuser password

#### Docker
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=j3d_db \
  -p 5432:5432 \
  postgres:15
```

### Creating Database

#### Using psql (Command Line)

```bash
# Connect as superuser
psql -U postgres

# Create database
CREATE DATABASE j3d_db;

# Create user
CREATE USER j3d_user WITH PASSWORD 'secure_password';

# Grant privileges
ALTER ROLE j3d_user SET client_encoding TO 'utf8';
ALTER ROLE j3d_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE j3d_user SET default_transaction_deferrable TO on;
ALTER ROLE j3d_user SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE j3d_db TO j3d_user;

# Connect as new user
\c j3d_db j3d_user

# Exit
\q
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: j3d_db
      POSTGRES_USER: j3d_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://j3d_user:secure_password@db:5432/j3d_db
    ports:
      - "5000:5000"
    depends_on:
      - db

volumes:
  postgres_data:
```

Start with:
```bash
docker-compose up
```

### Database Initialization

After creating database, initialize schema:

```bash
# Set environment variable
export DATABASE_URL="postgresql://j3d_user:secure_password@localhost/j3d_db"

# Run application to initialize
python app.py
```

Or manually:

```python
from app import app, db

# Set connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://j3d_user:secure_password@localhost/j3d_db'

with app.app_context():
    db.create_all()
    print("Database initialized")
```

## Database Schema

### Tables

#### user
```sql
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  etsy_user_id VARCHAR(255),
  username VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(255),
  shop_id VARCHAR(255),
  shop_name VARCHAR(255),
  jwt_token TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_etsy_user_id ON "user"(etsy_user_id);
CREATE INDEX idx_user_username ON "user"(username);
```

#### order
```sql
CREATE TABLE "order" (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  etsy_order_id VARCHAR(255) UNIQUE,
  buyer_name VARCHAR(255),
  buyer_email VARCHAR(255),
  status VARCHAR(50),
  production_status VARCHAR(50),
  total_amount NUMERIC(10,2),
  currency VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE INDEX idx_order_user_id ON "order"(user_id);
CREATE INDEX idx_order_status ON "order"(status);
CREATE INDEX idx_order_production_status ON "order"(production_status);
```

#### order_item
```sql
CREATE TABLE order_item (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  title VARCHAR(255),
  quantity INTEGER,
  price NUMERIC(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE
);

CREATE INDEX idx_order_item_order_id ON order_item(order_id);
```

#### order_note
```sql
CREATE TABLE order_note (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE
);

CREATE INDEX idx_order_note_order_id ON order_note(order_id);
```

#### order_communication
```sql
CREATE TABLE order_communication (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  message TEXT,
  direction VARCHAR(20),
  channel VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE
);

CREATE INDEX idx_order_communication_order_id ON order_communication(order_id);
```

#### filament
```sql
CREATE TABLE filament (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  material VARCHAR(100),
  color VARCHAR(100),
  initial_amount NUMERIC(10,2),
  current_amount NUMERIC(10,2),
  cost_per_gram NUMERIC(10,4),
  low_stock_threshold NUMERIC(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE INDEX idx_filament_user_id ON filament(user_id);
CREATE INDEX idx_filament_material ON filament(material);
```

#### printer
```sql
CREATE TABLE printer (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name VARCHAR(255),
  type VARCHAR(50),
  serial_number VARCHAR(100),
  connection_type VARCHAR(50),
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE INDEX idx_printer_user_id ON printer(user_id);
CREATE INDEX idx_printer_status ON printer(status);
```

#### printer_material
```sql
CREATE TABLE printer_material (
  id SERIAL PRIMARY KEY,
  printer_id INTEGER NOT NULL,
  slot INTEGER,
  material_type VARCHAR(100),
  color VARCHAR(100),
  weight_grams NUMERIC(10,2),
  remaining_pct INTEGER,
  vendor VARCHAR(255),
  cost_per_kg NUMERIC(10,2),
  loaded_at TIMESTAMP,
  last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (printer_id) REFERENCES printer(id) ON DELETE CASCADE
);

CREATE INDEX idx_printer_material_printer_id ON printer_material(printer_id);
```

#### scheduled_print
```sql
CREATE TABLE scheduled_print (
  id SERIAL PRIMARY KEY,
  printer_id INTEGER NOT NULL,
  job_name VARCHAR(255),
  file_name VARCHAR(255),
  material_type VARCHAR(100),
  material_slot INTEGER,
  estimated_duration_minutes INTEGER,
  priority INTEGER DEFAULT 0,
  status VARCHAR(50),
  scheduled_start TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (printer_id) REFERENCES printer(id) ON DELETE CASCADE
);

CREATE INDEX idx_scheduled_print_printer_id ON scheduled_print(printer_id);
CREATE INDEX idx_scheduled_print_status ON scheduled_print(status);
```

#### printer_notification
```sql
CREATE TABLE printer_notification (
  id SERIAL PRIMARY KEY,
  printer_id INTEGER UNIQUE NOT NULL,
  notify_print_start BOOLEAN DEFAULT TRUE,
  notify_print_complete BOOLEAN DEFAULT TRUE,
  notify_print_failed BOOLEAN DEFAULT TRUE,
  notify_material_change BOOLEAN DEFAULT TRUE,
  notify_maintenance BOOLEAN DEFAULT FALSE,
  email_enabled BOOLEAN DEFAULT FALSE,
  webhook_url TEXT,
  FOREIGN KEY (printer_id) REFERENCES printer(id) ON DELETE CASCADE
);
```

## Migrations

### Manual Migration (if needed)

If schema changes are needed:

```python
from app import app, db
from sqlalchemy import text

with app.app_context():
    # Example: Add new column
    db.session.execute(text('''
        ALTER TABLE filament 
        ADD COLUMN units VARCHAR(10) DEFAULT 'grams';
    '''))
    db.session.commit()
```

### Backup Before Migration

```bash
# PostgreSQL backup
pg_dump -U j3d_user j3d_db > backup_2025_01_01.sql

# Restore from backup
psql -U j3d_user j3d_db < backup_2025_01_01.sql
```

## Data Management

### Backup

#### PostgreSQL Backup

```bash
# Full backup
pg_dump -U j3d_user j3d_db > backup.sql

# Compressed backup
pg_dump -U j3d_user j3d_db | gzip > backup.sql.gz

# Restore
psql -U j3d_user j3d_db < backup.sql
```

#### SQLite Backup

```bash
# Simple copy
cp instance/app.db instance/app.db.backup

# Restore
cp instance/app.db.backup instance/app.db
```

### Cleanup Old Data

```python
from app import app, db
from models import Order
from datetime import datetime, timedelta

with app.app_context():
    # Delete orders older than 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    Order.query.filter(Order.created_at < six_months_ago).delete()
    db.session.commit()
```

### Export Data

```python
import csv
from app import app, db
from models import Order

with app.app_context():
    orders = Order.query.all()
    
    with open('orders_export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Order ID', 'Buyer', 'Status', 'Amount'])
        
        for order in orders:
            writer.writerow([
                order.etsy_order_id,
                order.buyer_name,
                order.status,
                order.total_amount
            ])
```

## Performance Tuning

### Connection Pooling

```python
# Configure in config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Query Optimization

```python
# Use eager loading for relationships
from sqlalchemy.orm import joinedload

orders = Order.query.options(
    joinedload(Order.items),
    joinedload(Order.notes)
).all()
```

### Indexing Strategy

Main indexes on:
- `user.username` - Login queries
- `order.user_id` - User's orders
- `order.status` - Status filtering
- `filament.user_id` - User's materials
- `printer.user_id` - User's printers

## Monitoring

### Check Connection

```bash
# PostgreSQL
psql -U j3d_user -h localhost j3d_db

# Should see prompt: j3d_db=>
```

### View Database Statistics

```sql
-- List all tables
\dt

-- View table size
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';

-- Count rows per table
SELECT 'order' as table_name, count(*) as rows FROM "order"
UNION ALL
SELECT 'user', count(*) FROM "user"
UNION ALL
SELECT 'filament', count(*) FROM filament
UNION ALL
SELECT 'printer', count(*) FROM printer;
```

### Connection Status

```python
from app import app, db

with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print("Database connected ✓")
    except Exception as e:
        print(f"Database error: {e}")
```

## Troubleshooting

### Connection Refused

**PostgreSQL not running:**
```bash
# Start PostgreSQL
sudo service postgresql start

# macOS
brew services start postgresql

# Docker
docker start postgres
```

### Permission Denied

**User doesn't have permissions:**
```sql
-- Connect as superuser
psql -U postgres j3d_db

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE j3d_db TO j3d_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO j3d_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO j3d_user;
```

### Database Lock

```sql
-- Kill long-running queries
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE usename = 'j3d_user' 
AND state = 'idle';
```

### Corrupted Index

```sql
-- Reindex specific table
REINDEX TABLE order;

-- Reindex all
REINDEX DATABASE j3d_db;
```

## Reference

### SQLAlchemy Documentation
- https://docs.sqlalchemy.org/

### PostgreSQL Documentation
- https://www.postgresql.org/docs/

### Database Design Best Practices
- Always use indexes on foreign keys
- Set NOT NULL on required fields
- Use CASCADE for related deletions
- Backup regularly
- Monitor query performance

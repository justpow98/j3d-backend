# 3D Print Shop Manager - Backend API

Flask-based REST API for managing Etsy shop orders, 3D printer management, and filament inventory tracking.

## Quick Links

- **[Getting Started](../GETTING_STARTED.md)** - 5-minute setup guide
- **[Deployment Guide](../DEPLOYMENT.md)** - Production setup for AWS/Heroku/DigitalOcean
- **[API Documentation](./docs/API.md)** - Complete REST API reference
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and data models
- **[Printer Setup Guide](./docs/PRINTER_SETUP.md)** - Bambu Lab, OctoPrint, Klipper integration

## Features

### Core Functionality
- ✅ **Etsy Integration** - OAuth authentication and real-time order sync
- ✅ **Order Management** - Track status, production queue, and fulfillment
- ✅ **Filament Inventory** - Material tracking with cost analysis
- ✅ **Printer Support** - Bambu Lab X1, OctoPrint, Klipper
- ✅ **Print Scheduling** - Queue management and automation
- ✅ **Analytics** - Business metrics and profitability

### Advanced Features
- 🔌 **Bambu Connect API** - Cloud and LAN mode printer control
- 📊 **AMS Material Tracking** - Automatic Material System monitoring
- 🔔 **Notifications** - Print events, material alerts, webhook support
- 📈 **Production Metrics** - Print history and efficiency tracking
- 🔐 **JWT Authentication** - Secure API access

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+ (or SQLite for development)
- Etsy API credentials from [etsy.com/developers](https://www.etsy.com/developers)

### Option 1: Docker (Recommended)
```bash
cd ..
docker-compose up -d
```
Access at `http://localhost:5000`

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your Etsy credentials

# Initialize database
python scripts/init_db.py --config development

# Run server
python app.py
```

Access at `http://localhost:5000`

## Configuration

### Environment Variables
See [.env.example](.env.example) for all options:

```env
# Required
ETSY_CLIENT_ID=your_id
ETSY_CLIENT_SECRET=your_secret
SECRET_KEY=generate_random_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/j3d_db

# Deployment
FRONTEND_URL=http://localhost:4200
BACKEND_URL=http://localhost:5000
```

## Database Setup

### Docker
Migrations run automatically on startup with `AUTO_MIGRATE=1`

### Manual
```bash
# Development with SQLite
python scripts/init_db.py --config development

# Production with PostgreSQL
python scripts/init_db.py --config production \
  --url postgresql://user:pass@host:5432/j3d_db

# Generate migrations (production)
python scripts/migrate_db.py --config production -m "Describe changes"
```

See [Database Documentation](./docs/DATABASE.md) for detailed info.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Get OAuth login URL
- `POST /api/auth/callback` - Handle OAuth callback
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/user` - Get current user info

### Orders
- `GET /api/orders` - List orders
- `GET /api/orders/:id` - Get order details
- `PUT /api/orders/:id` - Update order
- `POST /api/orders/sync` - Sync from Etsy
- `POST /api/orders/:id/notes` - Add note
- `POST /api/orders/:id/communications` - Log communication

### Filaments
- `GET /api/filaments` - List materials
- `POST /api/filaments` - Add material
- `PUT /api/filaments/:id` - Update material
- `DELETE /api/filaments/:id` - Remove material

### Printers (Bambu Connect)
- `GET /api/bambu/printers` - List printers
- `POST /api/bambu/printers` - Add printer
- `GET /api/bambu/printers/:id/status` - Printer status
- `GET /api/bambu/materials` - List AMS materials
- `PUT /api/bambu/materials/:id` - Update material
- `POST /api/bambu/notifications` - Configure alerts
- `POST /api/bambu/scheduled-prints` - Schedule print
- `GET /api/bambu/scheduled-prints` - List scheduled prints

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/revenue` - Revenue reports
- `GET /api/analytics/materials` - Material usage

See [API Documentation](./docs/API.md) for complete reference.

## Project Structure

```
j3d-backend/
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy database models
├── config.py                 # Configuration management
├── authentication.py         # OAuth and JWT handling
├── etsy_api.py              # Etsy API integration
├── scripts/                  # Database and utility scripts
├── migrations/              # Database migrations (Flask-Migrate)
├── instance/                # Instance-specific files
├── docs/                    # Documentation
│   ├── PRINTER_SETUP.md    # Printer integration guide
│   ├── API.md              # REST API reference
│   ├── ARCHITECTURE.md     # System design
│   └── DATABASE.md         # Database documentation
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container configuration
```

## Documentation

Full documentation is in the [docs/](./docs/) folder:

- **[PRINTER_SETUP.md](./docs/PRINTER_SETUP.md)** - How to integrate Bambu Lab, OctoPrint, Klipper
- **[API.md](./docs/API.md)** - Complete API endpoint reference
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Database schema and system design
- **[DATABASE.md](./docs/DATABASE.md)** - Database initialization and migrations

Additionally:
- **[../GETTING_STARTED.md](../GETTING_STARTED.md)** - Quick start for both backend and frontend
- **[../DEPLOYMENT.md](../DEPLOYMENT.md)** - Production deployment guide
- **[../CODE_CLEANUP_SUMMARY.md](../CODE_CLEANUP_SUMMARY.md)** - Code quality and standards

## Development

### Running Tests
```bash
pytest tests/
pytest tests/ -v  # Verbose output
```

### Code Style
```bash
# Format code
black .
flake8 .

# Type checking
mypy .
```

### Adding Features
1. Update `models.py` for schema changes
2. Create migration: `python scripts/migrate_db.py ... -m "Feature description"`
3. Add endpoints in `app.py`
4. Update API documentation
5. Test with frontend

## Printer Integration

### Bambu Lab X1
- Cloud API mode (requires Bambu account)
- LAN mode (local network only)
- AMS material slot tracking
- Real-time print monitoring
- Webhooks for notifications

### OctoPrint
- Remote HTTP API
- Print queue management
- Material assignment

### Klipper
- Moonraker API integration
- Custom macro support

See [PRINTER_SETUP.md](./docs/PRINTER_SETUP.md) for detailed setup.

## Troubleshooting

### Database Errors
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Reset database (⚠️ clears all data)
docker-compose down -v
docker-compose up -d
```

### OAuth Not Working
1. Verify Etsy Client ID/Secret are correct
2. Check redirect URI matches in Etsy app settings
3. Ensure `.env` file is loaded

### Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000
kill -9 <PID>
```

See [../DEPLOYMENT.md](../DEPLOYMENT.md) for more troubleshooting.

## Technology Stack

- **Framework**: Flask 3.0+ with SQLAlchemy ORM
- **Database**: PostgreSQL 15+ (SQLite for dev)
- **Authentication**: JWT + Etsy OAuth 2.0
- **APIs**: RESTful with CORS support
- **Container**: Docker & Docker Compose
- **Migration**: Flask-Migrate (Alembic)

## Performance

- 🚀 **Fast**: Optimized queries and caching
- 📊 **Scalable**: Designed for 1000+ orders/month
- 🔄 **Reliable**: Transaction support and error recovery
- 🔐 **Secure**: Input validation and SQL injection prevention

## Security

- ✅ JWT token authentication
- ✅ OAuth 2.0 with Etsy
- ✅ HTTPS/TLS support
- ✅ Input validation
- ✅ CORS configuration
- ✅ Rate limiting ready
- ✅ Secure password hashing (not used for user auth)

## License

MIT - Free to use and modify

## Support

- 📖 [Getting Started](../GETTING_STARTED.md)
- 📚 [Full Documentation](./docs/)
- 🐛 [Report Issues](../../issues)
- 💬 See [../README.md](../README.md) for general project info

---

**Ready to manage your 3D printing business?** Start with [Getting Started](../GETTING_STARTED.md) or jump to [Deployment](../DEPLOYMENT.md) for production setup.
````

#### Quick start (dev/test - simple create_all)
```bash
# Dev sqlite
python scripts/init_db.py --config development

# Test sqlite
python scripts/init_db.py --config testing

# Production Postgres (creates tables, no migration tracking)
python scripts/init_db.py --config production --url postgresql://USER:PASS@HOST:PORT/DBNAME
```

#### Migrations (recommended for production)
```bash
# 1. Generate migration for schema changes
python scripts/migrate_db.py --config development -m "Add printers and CRM tables"

# 2. Apply migrations
python scripts/migrate_db.py --config development --apply

# Or do both at once
python scripts/migrate_db.py --config production --url postgresql://USER:PASS@HOST:PORT/DBNAME -m "Initial schema" --apply

# Use migrations with init_db
python scripts/init_db.py --config production --url postgresql://... --migrate
```

**Notes:**
- `init_db.py`: Simple table creation via `create_all()` (default) or apply existing migrations (`--migrate`).
- `migrate_db.py`: Generate and optionally apply migrations (tracks schema changes properly).
- The scripts auto-normalize `postgres://` → `postgresql://`.
- Ensure the Postgres database exists before running.

### Auto schema setup on app start (non-containerized)

- Dev/test (default): `AUTO_DB_CREATE` is enabled; app runs `create_all()` on startup. Disable via `AUTO_DB_CREATE=0`.
- Prod: `AUTO_DB_CREATE` is disabled. To apply migrations on start (when present), set `RUN_DB_UPGRADE=1`; the app calls `flask_migrate.upgrade()` during startup. Leave unset for manual control.

## 🐳 Docker

Pull and run the latest image:
```bash
docker pull ghcr.io/justpow98/j3d-backend:latest
docker run -d -p 5000:5000 --env-file .env ghcr.io/justpow98/j3d-backend:latest
```

Or use Docker Compose:
```bash
docker-compose up -d
```

## 📦 Available Images

- `ghcr.io/justpow98/j3d-backend:latest` - Latest main branch build
- `ghcr.io/justpow98/j3d-backend:main` - Main branch
- `ghcr.io/justpow98/j3d-backend:main-<sha>` - Specific commit

---

**Note:** Replace `justpow98` and `j3d-backend` with your actual GitHub username and repository name.
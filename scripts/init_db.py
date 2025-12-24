import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import _normalize_db_url
from app import create_app
from models import db
from flask_migrate import upgrade as migrate_upgrade


def main():
    parser = argparse.ArgumentParser(description="Initialize database tables for J3D backend")
    parser.add_argument("--config", default="development", help="App config name (development, production, testing)")
    parser.add_argument("--url", dest="url", default=os.getenv("DATABASE_URL"), help="Database URL; defaults to env DATABASE_URL or sqlite for dev")
    parser.add_argument("--migrate", action="store_true", help="Use migrations instead of create_all (recommended for production)")
    args = parser.parse_args()

    db_url = _normalize_db_url(args.url) if args.url else None
    if db_url:
        os.environ["DATABASE_URL"] = db_url

    app = create_app(args.config)
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    with app.app_context():
        if args.migrate and migrations_dir.exists():
            print("Applying migrations...")
            migrate_upgrade(directory=str(migrations_dir))
            print(f"✓ Migrations applied")
        else:
            db.create_all()
            print(f"✓ Created tables via create_all()")
        
        print(f"Database ready: config={args.config} at {app.config['SQLALCHEMY_DATABASE_URI']}")


if __name__ == "__main__":
    main()

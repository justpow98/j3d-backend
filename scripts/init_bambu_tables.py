#!/usr/bin/env python
"""
Initialize Bambu Connect tables for development
Run this after updating models.py if using SQLite without migrations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import BambuMaterial, PrintNotification, ScheduledPrint

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        try:
            # Create tables if they don't exist
            print("Creating Bambu Connect tables...")
            BambuMaterial.__table__.create(db.engine, checkfirst=True)
            PrintNotification.__table__.create(db.engine, checkfirst=True)
            ScheduledPrint.__table__.create(db.engine, checkfirst=True)
            
            print("✓ BambuMaterial table created")
            print("✓ PrintNotification table created")
            print("✓ ScheduledPrint table created")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\nAvailable tables:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            print("\n✓ All Bambu Connect tables initialized successfully!")
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            sys.exit(1)

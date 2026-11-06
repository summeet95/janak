"""
Database initialization script.
Creates the local SQLite database used by the inventory app.
"""

from app import create_app, mongo


def init_database():
    """Initialize SQLite database tables."""
    app = create_app('development')

    with app.app_context():
        mongo.db.init_schema()
        print("SQLite database initialized successfully.")
        print(f"Database file: {app.config['SQLITE_PATH']}")

    return True


if __name__ == '__main__':
    print("=" * 50)
    print("SQLite Database Initialization")
    print("=" * 50)
    print()

    init_database()
    print("\nYou can now run: python run.py")

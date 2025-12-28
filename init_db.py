"""Initialize database"""
from app import app, db
from models import Message, User, AnalyticsSummary

def init_database():
    """Create all database tables"""
    with app.app_context():
        # Drop all tables (caution: deletes all data)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        print("✅ Database initialized successfully!")
        print(f"📁 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()

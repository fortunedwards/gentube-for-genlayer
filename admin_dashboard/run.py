#!/usr/bin/env python3
"""
Simple startup script for GenTube admin dashboard
"""
import os
from app import app, db, User

def setup_database():
    """Initialize database and create admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("[OK] Database tables created")
        
        # Create admin user if doesn't exist
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if not User.query.filter_by(username=admin_username).first():
            admin = User(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"[OK] Admin user created: {admin_username}")
        else:
            print(f"[OK] Admin user exists: {admin_username}")

if __name__ == '__main__':
    print("GenTube Admin Dashboard")
    print("=" * 30)
    
    # Setup database
    setup_database()
    
    print("\n[INFO] Starting server...")
    print("[INFO] Access at: http://localhost:5000")
    print("[INFO] Default login: admin / admin123")
    print("\n[WARNING] Change default credentials in production!")
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
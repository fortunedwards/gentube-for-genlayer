import sys
import os
from pathlib import Path

# Add admin_dashboard to Python path
current_dir = Path(__file__).parent
admin_dir = current_dir.parent / 'admin_dashboard'
sys.path.insert(0, str(admin_dir))

# Set working directory to admin_dashboard
os.chdir(str(admin_dir))

# Import the complete Flask app
from app import app, db, create_admin_user

# Initialize database and admin user for serverless
try:
    with app.app_context():
        db.create_all()
        create_admin_user()
except Exception as e:
    print(f"Database initialization error: {e}")

# Vercel handler
def handler(event, context):
    return app

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
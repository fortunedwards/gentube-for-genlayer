import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'admin_dashboard'))

from app import app, db, create_admin_user

# Initialize database for serverless
with app.app_context():
    db.create_all()
    create_admin_user()

def handler(request, context):
    return app
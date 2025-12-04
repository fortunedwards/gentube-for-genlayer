import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for production
os.environ.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-key-change-in-production'))
os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', 'sqlite:///tmp/videos.db'))
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # Import your complete Flask application
    from app import app, db, create_admin_user
    
    # Initialize database for serverless environment
    with app.app_context():
        db.create_all()
        create_admin_user()
        
except ImportError as e:
    # Fallback to simple Flask app if imports fail
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return f'''
        <h1>Admin Dashboard</h1>
        <p>Import Error: {str(e)}</p>
        <p>Some dependencies may be missing. Check the logs.</p>
        '''

if __name__ == '__main__':
    app.run(debug=True)
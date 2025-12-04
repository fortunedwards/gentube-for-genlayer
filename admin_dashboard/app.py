from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import bcrypt
from datetime import datetime, timedelta
import json
import csv
import io
import os
from dotenv import load_dotenv
from functools import wraps
from forms import VideoForm, BulkImportForm
from backup import BackupManager
from bulk_operations import BulkOperations
from video_metadata import VideoMetadataExtractor
from webhooks import WebhookManager, initialize_default_webhooks

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/videos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app, origins=['*'])

# Initialize rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Initialize backup system
backup_manager = BackupManager('instance/videos.db')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    speaker = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(500), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    video_metadata = db.Column(db.JSON)  # Store video metadata
    view_count = db.Column(db.Integer, default=0)  # Track views

def login_required_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required_jwt
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required_jwt
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get paginated videos
    videos = Video.query.order_by(Video.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('dashboard.html', 
                         videos=videos.items,
                         pagination=videos)

@app.route('/add_video', methods=['GET', 'POST'])
@login_required_jwt
def add_video():
    form = VideoForm()
    if form.validate_on_submit():
        # Extract metadata
        metadata = {}
        try:
            extractor = VideoMetadataExtractor()
            metadata = extractor.extract(form.url.data)
        except Exception as e:
            metadata = {'extraction_error': str(e)}
        
        video = Video(
            title=form.title.data,
            url=form.url.data,
            speaker=form.speaker.data,
            tags=form.tags.data or '',
            description=form.description.data or '',
            video_metadata=metadata
        )
        db.session.add(video)
        db.session.commit()
        
        # Trigger webhook
        WebhookManager.trigger_webhook('video.created', {
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'speaker': video.speaker
        })
        
        flash('Video added successfully!')
        if metadata and 'extraction_error' not in metadata:
            flash(f'Metadata extracted from {metadata.get("platform", "unknown")} platform')
        return redirect(url_for('dashboard'))
    return render_template('add_video.html', form=form)

@app.route('/edit_video/<int:id>', methods=['GET', 'POST'])
@login_required_jwt
def edit_video(id):
    video = Video.query.get_or_404(id)
    form = VideoForm(obj=video)
    if form.validate_on_submit():
        old_url = video.url
        form.populate_obj(video)
        
        # Re-extract metadata if URL changed
        if old_url != video.url:
            try:
                extractor = VideoMetadataExtractor()
                video.video_metadata = extractor.extract(video.url)
            except Exception as e:
                video.video_metadata = getattr(video, 'video_metadata', {})
                video.video_metadata['extraction_error'] = str(e)
        
        db.session.commit()
        
        # Trigger webhook
        WebhookManager.trigger_webhook('video.updated', {
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'speaker': video.speaker
        })
        
        flash('Video updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('edit_video.html', form=form, video=video)

@app.route('/delete_video/<int:id>')
@login_required_jwt
def delete_video(id):
    video = Video.query.get_or_404(id)
    
    # Store info for webhook
    video_info = {
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'speaker': video.speaker
    }
    
    db.session.delete(video)
    db.session.commit()
    
    # Trigger webhook
    WebhookManager.trigger_webhook('video.deleted', video_info)
    
    flash('Video deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/export_data')
@login_required_jwt
def export_data():
    json_data = BulkOperations.export_to_json(Video)
    video_data = json.loads(json_data)
    
    # Write to a temporary file for download
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_data)
        temp_path = f.name
    
    flash(f'Data exported successfully! {len(video_data)} videos exported.')
    flash('Use the API endpoint /api/videos to get JSON data for your public site.')
    return redirect(url_for('dashboard'))

@app.route('/api/videos')
@login_required_jwt
def api_videos():
    """API endpoint to get videos JSON for public site"""
    json_data = BulkOperations.export_to_json(Video)
    response = make_response(json_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/export_json')
@login_required_jwt
def export_json():
    json_data = BulkOperations.export_to_json(Video)
    response = make_response(json_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=videos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    return response

@app.route('/export_csv')
@login_required_jwt
def export_csv():
    csv_data = BulkOperations.export_to_csv(Video)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=videos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return response

@app.route('/bulk_import', methods=['GET', 'POST'])
@login_required_jwt
def bulk_import():
    form = BulkImportForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            try:
                json_data = file.read().decode('utf-8')
                results = BulkOperations.import_from_json(json_data, db, Video)
                
                if results['success'] > 0:
                    flash(f'Successfully imported {results["success"]} videos!')
                if results['skipped'] > 0:
                    flash(f'Skipped {results["skipped"]} duplicate videos.')
                if results['errors']:
                    for error in results['errors'][:5]:  # Show first 5 errors
                        flash(f'Error: {error}', 'error')
                
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Import failed: {str(e)}', 'error')
    
    return render_template('bulk_import.html', form=form)

@app.route('/backup_database')
@login_required_jwt
def backup_database():
    backup_path = backup_manager.create_backup()
    if backup_path:
        flash('Database backup created successfully!')
    else:
        flash('Backup failed!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/manage_backups')
@login_required_jwt
def manage_backups():
    backups = backup_manager.list_backups()
    return render_template('manage_backups.html', backups=backups)

@app.route('/restore_backup/<filename>')
@login_required_jwt
def restore_backup(filename):
    if backup_manager.restore_backup(filename):
        flash(f'Database restored from {filename}!')
    else:
        flash('Restore failed!', 'error')
    return redirect(url_for('manage_backups'))

@app.route('/bulk_delete', methods=['POST'])
@login_required_jwt
def bulk_delete():
    video_ids = request.form.getlist('video_ids')
    if video_ids:
        video_ids = [int(id) for id in video_ids]
        result = BulkOperations.bulk_delete(video_ids, db, Video)
        if result['success']:
            flash(f'Successfully deleted {result["deleted"]} videos!')
        else:
            flash(f'Delete failed: {result["error"]}', 'error')
    return redirect(url_for('dashboard'))

def create_admin_user():
    with app.app_context():
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if not User.query.filter_by(username=admin_username).first():
            admin = User(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: username={admin_username}")

@app.context_processor
def inject_auth_status():
    return {'is_authenticated': 'user_id' in session}

@app.route('/api/metadata/extract', methods=['POST'])
@login_required_jwt
def extract_metadata_endpoint():
    """Extract metadata from URL"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        extractor = VideoMetadataExtractor()
        metadata = extractor.extract(data['url'])
        return jsonify({'metadata': metadata})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video/<int:video_id>/view')
def view_video(video_id):
    """Track video view and show preview"""
    video = Video.query.get_or_404(video_id)
    
    # Increment view count
    if not video.view_count:
        video.view_count = 0
    video.view_count += 1
    db.session.commit()
    
    return render_template('video_preview.html', video=video)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Start automated backups (every 24 hours)
        backup_manager.start_scheduled_backups(24)
        
        # Initialize default webhooks
        initialize_default_webhooks()
        
    app.run(debug=True)
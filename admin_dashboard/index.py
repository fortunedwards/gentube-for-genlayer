from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import os
import bcrypt
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tmp/videos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
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
    view_count = db.Column(db.Integer, default=0)

# Initialize database
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(username='admin')
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    videos = Video.query.order_by(Video.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template_string(DASHBOARD_TEMPLATE, videos=videos.items, pagination=videos)

@app.route('/add_video', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        video = Video(
            title=request.form.get('title'),
            url=request.form.get('url'),
            speaker=request.form.get('speaker'),
            tags=request.form.get('tags', ''),
            description=request.form.get('description', '')
        )
        db.session.add(video)
        db.session.commit()
        flash('Video added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template_string(ADD_VIDEO_TEMPLATE)

@app.route('/delete_video/<int:video_id>')
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/api/videos')
def api_videos():
    videos = Video.query.all()
    video_list = []
    for video in videos:
        video_list.append({
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'speaker': video.speaker,
            'tags': video.tags,
            'description': video.description,
            'date_added': video.date_added.isoformat() if video.date_added else None,
            'view_count': video.view_count or 0
        })
    return jsonify(video_list)

@app.route('/export_json')
@login_required
def export_json():
    videos = Video.query.all()
    video_list = []
    for video in videos:
        video_list.append({
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'speaker': video.speaker,
            'tags': video.tags,
            'description': video.description,
            'date_added': video.date_added.isoformat() if video.date_added else None,
            'view_count': video.view_count or 0
        })
    
    response = make_response(json.dumps(video_list, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=videos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    return response

@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    if request.method == 'POST':
        video.title = request.form.get('title')
        video.url = request.form.get('url')
        video.speaker = request.form.get('speaker')
        video.tags = request.form.get('tags', '')
        video.description = request.form.get('description', '')
        
        db.session.commit()
        flash('Video updated successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template_string(EDIT_VIDEO_TEMPLATE, video=video)

@app.route('/bulk_import', methods=['GET', 'POST'])
@login_required
def bulk_import():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and file.filename.endswith('.json'):
            try:
                data = json.loads(file.read().decode('utf-8'))
                imported = 0
                skipped = 0
                
                for item in data:
                    # Check if video already exists
                    existing = Video.query.filter_by(url=item.get('url')).first()
                    if existing:
                        skipped += 1
                        continue
                    
                    video = Video(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        speaker=item.get('speaker', ''),
                        tags=item.get('tags', ''),
                        description=item.get('description', '')
                    )
                    db.session.add(video)
                    imported += 1
                
                db.session.commit()
                flash(f'Successfully imported {imported} videos, skipped {skipped} duplicates')
                
            except Exception as e:
                flash(f'Import failed: {str(e)}')
        else:
            flash('Please upload a JSON file')
        
        return redirect(url_for('dashboard'))
    
    return render_template_string(BULK_IMPORT_TEMPLATE)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>GenTube Admin - Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full space-y-8">
        <div class="text-center">
            <h2 class="text-3xl font-bold">GenTube Admin</h2>
            <p class="mt-2 text-gray-400">Sign in to your account</p>
        </div>
        <form method="POST" class="mt-8 space-y-6">
            <div class="space-y-4">
                <input name="username" type="text" required 
                       class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white" 
                       placeholder="Username">
                <input name="password" type="password" required 
                       class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white" 
                       placeholder="Password">
            </div>
            <button type="submit" 
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Sign In
            </button>
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="bg-red-600 text-white p-3 rounded">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>GenTube Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-xl font-bold">GenTube Admin</h1>
            <div class="space-x-4">
                <a href="{{ url_for('add_video') }}" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">Add Video</a>
                <a href="{{ url_for('bulk_import') }}" class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded">Import</a>
                <a href="{{ url_for('export_json') }}" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded">Export</a>
                <a href="{{ url_for('logout') }}" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mx-auto px-4 py-8">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="bg-green-600 text-white p-3 rounded mb-4">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-4">Videos ({{ videos|length }})</h2>
            
            {% if videos %}
                <div class="space-y-4">
                    {% for video in videos %}
                    <div class="bg-gray-700 p-4 rounded flex justify-between items-start">
                        <div class="flex-1">
                            <h3 class="font-semibold text-lg">{{ video.title }}</h3>
                            <p class="text-gray-300">Speaker: {{ video.speaker }}</p>
                            <p class="text-gray-400 text-sm">Tags: {{ video.tags }}</p>
                            <a href="{{ video.url }}" target="_blank" class="text-blue-400 hover:text-blue-300">{{ video.url }}</a>
                            {% if video.description %}
                                <p class="text-gray-300 mt-2">{{ video.description }}</p>
                            {% endif %}
                        </div>
                        <div class="flex space-x-2">
                            <a href="{{ url_for('edit_video', video_id=video.id) }}" 
                               class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">Edit</a>
                            <a href="{{ url_for('delete_video', video_id=video.id) }}" 
                               class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                               onclick="return confirm('Delete this video?')">Delete</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <p class="text-gray-400">No videos added yet. <a href="{{ url_for('add_video') }}" class="text-blue-400">Add your first video</a></p>
            {% endif %}
        </div>
        
        <div class="mt-8 text-center">
            <a href="https://gentube-for-genlayer.vercel.app/" 
               class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded">
                View Public Site
            </a>
        </div>
    </div>
</body>
</html>
'''

ADD_VIDEO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Add Video - GenTube Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-xl font-bold">GenTube Admin</h1>
            <a href="{{ url_for('dashboard') }}" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded">Back to Dashboard</a>
        </div>
    </nav>
    
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-6">Add New Video</h2>
            
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Title</label>
                    <input name="title" type="text" required 
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">URL</label>
                    <input name="url" type="url" required 
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                           placeholder="https://youtube.com/watch?v=...">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Speaker</label>
                    <input name="speaker" type="text" required 
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Tags</label>
                    <input name="tags" type="text" 
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                           placeholder="blockchain, AI, tutorial">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Description</label>
                    <textarea name="description" rows="4" 
                              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"></textarea>
                </div>
                
                <button type="submit" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Add Video
                </button>
            </form>
        </div>
    </div>
</body>
</html>
'''

EDIT_VIDEO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Edit Video - GenTube Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-xl font-bold">GenTube Admin</h1>
            <a href="{{ url_for('dashboard') }}" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded">Back to Dashboard</a>
        </div>
    </nav>
    
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-6">Edit Video</h2>
            
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Title</label>
                    <input name="title" type="text" required value="{{ video.title }}"
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">URL</label>
                    <input name="url" type="url" required value="{{ video.url }}"
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Speaker</label>
                    <input name="speaker" type="text" required value="{{ video.speaker }}"
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Tags</label>
                    <input name="tags" type="text" value="{{ video.tags }}"
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Description</label>
                    <textarea name="description" rows="4" 
                              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">{{ video.description }}</textarea>
                </div>
                
                <button type="submit" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Update Video
                </button>
            </form>
        </div>
    </div>
</body>
</html>
'''

BULK_IMPORT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bulk Import - GenTube Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 p-4">
        <div class="flex justify-between items-center">
            <h1 class="text-xl font-bold">GenTube Admin</h1>
            <a href="{{ url_for('dashboard') }}" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded">Back to Dashboard</a>
        </div>
    </nav>
    
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-bold mb-6">Bulk Import Videos</h2>
            
            <div class="bg-gray-700 p-4 rounded mb-6">
                <h3 class="font-semibold mb-2">JSON Format Expected:</h3>
                <pre class="text-sm text-gray-300">[\n  {\n    "title": "Video Title",\n    "url": "https://youtube.com/watch?v=...",\n    "speaker": "Speaker Name",\n    "tags": "tag1, tag2",\n    "description": "Video description"\n  }\n]</pre>
            </div>
            
            <form method="POST" enctype="multipart/form-data" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Select JSON File</label>
                    <input name="file" type="file" accept=".json" required
                           class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                </div>
                
                <button type="submit" 
                        class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
                    Import Videos
                </button>
            </form>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
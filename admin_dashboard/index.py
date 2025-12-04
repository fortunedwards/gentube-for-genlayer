from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash, session
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Simple in-memory storage
videos = []
users = {'admin': 'admin123'}  # username: password

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
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
    return render_template_string(DASHBOARD_TEMPLATE, videos=videos)

@app.route('/add_video', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        video = {
            'id': len(videos) + 1,
            'title': request.form.get('title'),
            'url': request.form.get('url'),
            'speaker': request.form.get('speaker'),
            'tags': request.form.get('tags', ''),
            'description': request.form.get('description', ''),
            'date_added': datetime.now().isoformat()
        }
        videos.append(video)
        flash('Video added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template_string(ADD_VIDEO_TEMPLATE)

@app.route('/delete_video/<int:video_id>')
@login_required
def delete_video(video_id):
    global videos
    videos = [v for v in videos if v['id'] != video_id]
    flash('Video deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/api/videos')
def api_videos():
    return jsonify(videos)

@app.route('/export_json')
@login_required
def export_json():
    from flask import make_response
    response = make_response(json.dumps(videos, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=videos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    return response

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
                        <a href="{{ url_for('delete_video', video_id=video.id) }}" 
                           class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm ml-4"
                           onclick="return confirm('Delete this video?')">Delete</a>
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

if __name__ == '__main__':
    app.run(debug=True)
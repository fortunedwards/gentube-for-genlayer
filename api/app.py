from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import json
import os
import sys
from datetime import datetime

# Add admin_dashboard to path to import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'admin_dashboard'))

from forms import VideoForm, BulkImportForm

app = Flask(__name__, 
           template_folder='../admin_dashboard/templates',
           static_folder='../admin_dashboard/static')
app.secret_key = 'your-secret-key-change-in-production'

def load_videos():
    try:
        with open('../public_archive/videos.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_videos(videos):
    with open('../public_archive/videos.json', 'w') as f:
        json.dump(videos, f, indent=2)

@app.route('/admin')
@app.route('/admin/')
def dashboard():
    videos = load_videos()
    return render_template('dashboard.html', videos=videos, is_authenticated=True)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_video():
    form = VideoForm()
    if form.validate_on_submit():
        videos = load_videos()
        video = {
            'id': max([v.get('id', 0) for v in videos], default=0) + 1,
            'title': form.title.data,
            'url': form.url.data,
            'speaker': form.speaker.data,
            'tags': [tag.strip() for tag in form.tags.data.split(',') if tag.strip()] if form.tags.data else [],
            'description': form.description.data or '',
            'date_added': datetime.now().isoformat()
        }
        videos.append(video)
        save_videos(videos)
        flash('Video added successfully!', 'success')
        return redirect('/admin')
    
    return render_template('add_video.html', form=form, is_authenticated=True)

@app.route('/admin/edit/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    videos = load_videos()
    video = next((v for v in videos if v.get('id') == video_id), None)
    
    if not video:
        flash('Video not found', 'error')
        return redirect('/admin')
    
    form = VideoForm(obj=type('obj', (object,), video)())
    if form.validate_on_submit():
        video.update({
            'title': form.title.data,
            'url': form.url.data,
            'speaker': form.speaker.data,
            'tags': [tag.strip() for tag in form.tags.data.split(',') if tag.strip()] if form.tags.data else [],
            'description': form.description.data or ''
        })
        save_videos(videos)
        flash('Video updated successfully!', 'success')
        return redirect('/admin')
    
    return render_template('edit_video.html', form=form, video=video, is_authenticated=True)

@app.route('/admin/preview/<int:video_id>')
def video_preview(video_id):
    videos = load_videos()
    video = next((v for v in videos if v.get('id') == video_id), None)
    
    if not video:
        flash('Video not found', 'error')
        return redirect('/admin')
    
    # Convert to object for template compatibility
    video_obj = type('Video', (), {
        **video,
        'date_added': datetime.fromisoformat(video['date_added'].replace('Z', '+00:00')) if video.get('date_added') else datetime.now()
    })()
    
    return render_template('video_preview.html', video=video_obj, is_authenticated=True)

@app.route('/admin/delete/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    videos = load_videos()
    videos = [v for v in videos if v.get('id') != video_id]
    save_videos(videos)
    flash('Video deleted successfully!', 'success')
    return redirect('/admin')

# API endpoints for the public archive
@app.route('/api/videos', methods=['GET'])
def api_get_videos():
    return jsonify(load_videos())

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)
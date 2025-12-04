from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

def load_videos():
    try:
        with open('public_archive/videos.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_videos(videos):
    with open('public_archive/videos.json', 'w') as f:
        json.dump(videos, f, indent=2)

@app.route('/api/videos', methods=['GET'])
def api_get_videos():
    return jsonify(load_videos())

@app.route('/api/videos', methods=['POST'])
def api_add_video():
    data = request.json
    videos = load_videos()
    video = {
        'id': max([v.get('id', 0) for v in videos], default=0) + 1,
        'title': data.get('title'),
        'url': data.get('url'),
        'speaker': data.get('speaker'),
        'tags': data.get('tags', []),
        'description': data.get('description', ''),
        'date_added': datetime.now().isoformat()
    }
    videos.append(video)
    save_videos(videos)
    return jsonify(video), 201

# Vercel handler
def handler(request, context):
    return app(request, context)
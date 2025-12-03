from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

def handler(req):
    with app.app_context():
        if req.method == 'GET':
            try:
                with open('public_archive/videos.json', 'r') as f:
                    videos = json.load(f)
                return jsonify(videos)
            except:
                return jsonify([])
        
        elif req.method == 'POST':
            data = req.get_json()
            video = {
                'id': len(get_videos()) + 1,
                'title': data.get('title'),
                'url': data.get('url'),
                'speaker': data.get('speaker'),
                'tags': data.get('tags', []),
                'description': data.get('description', ''),
                'date_added': data.get('date_added')
            }
            
            try:
                with open('public_archive/videos.json', 'r') as f:
                    videos = json.load(f)
            except:
                videos = []
            
            videos.append(video)
            
            with open('public_archive/videos.json', 'w') as f:
                json.dump(videos, f, indent=2)
            
            return jsonify(video), 201

def get_videos():
    try:
        with open('public_archive/videos.json', 'r') as f:
            return json.load(f)
    except:
        return []
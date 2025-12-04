#!/usr/bin/env python3
import json
from datetime import datetime

def add_video():
    # Load existing videos
    try:
        with open('public_archive/videos.json', 'r') as f:
            videos = json.load(f)
    except:
        videos = []
    
    # Get new video info
    title = input("Title: ")
    url = input("URL: ")
    speaker = input("Speaker: ")
    tags = input("Tags (comma-separated): ").split(',')
    description = input("Description: ")
    
    # Create new video
    new_video = {
        "id": max([v.get('id', 0) for v in videos], default=0) + 1,
        "title": title,
        "url": url,
        "speaker": speaker,
        "tags": [tag.strip() for tag in tags if tag.strip()],
        "date_added": datetime.now().isoformat(),
        "description": description
    }
    
    # Add and save
    videos.append(new_video)
    with open('public_archive/videos.json', 'w') as f:
        json.dump(videos, f, indent=2)
    
    print(f"✅ Added: {title}")

if __name__ == "__main__":
    add_video()
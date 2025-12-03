import json
import csv
from datetime import datetime
from flask import current_app
import validators

class BulkOperations:
    @staticmethod
    def validate_video_data(video_data):
        """Validate video data structure"""
        required_fields = ['title', 'url', 'speaker']
        errors = []
        
        for field in required_fields:
            if not video_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        if video_data.get('title') and len(video_data['title']) > 200:
            errors.append("Title too long (max 200 characters)")
        
        if video_data.get('url') and not validators.url(video_data['url']):
            errors.append("Invalid URL format")
        
        if video_data.get('speaker') and len(video_data['speaker']) > 100:
            errors.append("Speaker name too long (max 100 characters)")
        
        return errors
    
    @staticmethod
    def import_from_json(json_data, db, Video):
        """Import videos from JSON data"""
        results = {'success': 0, 'errors': [], 'skipped': 0}
        
        try:
            videos_data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            for i, video_data in enumerate(videos_data):
                errors = BulkOperations.validate_video_data(video_data)
                
                if errors:
                    results['errors'].append(f"Row {i+1}: {', '.join(errors)}")
                    continue
                
                # Check if video already exists
                existing = Video.query.filter_by(url=video_data['url']).first()
                if existing:
                    results['skipped'] += 1
                    continue
                
                # Create new video
                video = Video(
                    title=video_data['title'],
                    url=video_data['url'],
                    speaker=video_data['speaker'],
                    tags=video_data.get('tags', ''),
                    description=video_data.get('description', '')
                )
                db.session.add(video)
                results['success'] += 1
            
            db.session.commit()
            
        except json.JSONDecodeError:
            results['errors'].append("Invalid JSON format")
        except Exception as e:
            db.session.rollback()
            results['errors'].append(f"Import failed: {str(e)}")
        
        return results
    
    @staticmethod
    def export_to_json(Video):
        """Export all videos to JSON"""
        videos = Video.query.all()
        video_data = []
        
        for video in videos:
            tags = [tag.strip() for tag in video.tags.split(',') if tag.strip()] if video.tags else []
            video_data.append({
                'id': video.id,
                'title': video.title,
                'url': video.url,
                'speaker': video.speaker,
                'tags': tags,
                'date_added': video.date_added.isoformat(),
                'description': video.description or ''
            })
        
        return json.dumps(video_data, indent=2)
    
    @staticmethod
    def export_to_csv(Video):
        """Export all videos to CSV format"""
        videos = Video.query.all()
        csv_data = []
        
        # Header
        csv_data.append(['ID', 'Title', 'URL', 'Speaker', 'Tags', 'Date Added', 'Description'])
        
        # Data rows
        for video in videos:
            tags = ', '.join([tag.strip() for tag in video.tags.split(',') if tag.strip()]) if video.tags else ''
            csv_data.append([
                video.id,
                video.title,
                video.url,
                video.speaker,
                tags,
                video.date_added.strftime('%Y-%m-%d %H:%M:%S'),
                video.description or ''
            ])
        
        return csv_data
    
    @staticmethod
    def bulk_delete(video_ids, db, Video):
        """Delete multiple videos by IDs"""
        try:
            deleted_count = Video.query.filter(Video.id.in_(video_ids)).delete(synchronize_session=False)
            db.session.commit()
            return {'success': True, 'deleted': deleted_count}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
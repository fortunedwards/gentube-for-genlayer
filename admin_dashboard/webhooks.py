import json
import os
from datetime import datetime

class WebhookManager:
    """Simple webhook manager for auto-export functionality"""
    
    @staticmethod
    def trigger_webhook(event, data):
        """Trigger webhook for auto-export"""
        if event in ['video.created', 'video.updated', 'video.deleted']:
            PublicArchiveWebhook.trigger_export(event, data)

class PublicArchiveWebhook:
    """Auto-export webhook for public archive updates"""
    
    @staticmethod
    def trigger_export(event, data):
        """Trigger automatic export to public archive"""
        try:
            from bulk_operations import BulkOperations
            from app import Video
            
            # Export to public archive
            json_data = BulkOperations.export_to_json(Video)
            public_path = os.path.join('..', 'public_archive', 'videos.json')
            
            with open(public_path, 'w') as f:
                f.write(json_data)
            
            print(f"Auto-export completed: {len(json.loads(json_data))} videos")
            return True
        except Exception as e:
            print(f"Auto-export failed: {str(e)}")
            return False

def initialize_default_webhooks():
    """Initialize default webhooks"""
    print("Auto-export webhook initialized")
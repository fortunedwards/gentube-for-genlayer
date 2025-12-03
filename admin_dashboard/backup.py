import os
import shutil
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

class BackupManager:
    def __init__(self, db_path, backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.scheduler = BackgroundScheduler()
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """Create a backup of the database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'videos_backup_{timestamp}.db'
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Keep only last 10 backups
            self.cleanup_old_backups()
            
            print(f"[BACKUP] Database backed up to {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return None
    
    def cleanup_old_backups(self, keep_count=10):
        """Keep only the most recent backups"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('videos_backup_')]
            backups.sort(reverse=True)
            
            for backup in backups[keep_count:]:
                os.remove(os.path.join(self.backup_dir, backup))
                print(f"[CLEANUP] Removed old backup: {backup}")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
    
    def start_scheduled_backups(self, interval_hours=24):
        """Start automatic backups"""
        self.scheduler.add_job(
            func=self.create_backup,
            trigger="interval",
            hours=interval_hours,
            id='backup_job'
        )
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())
        print(f"[BACKUP] Scheduled backups every {interval_hours} hours")
    
    def restore_backup(self, backup_filename):
        """Restore from a backup file"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.db_path)
                print(f"[RESTORE] Database restored from {backup_filename}")
                return True
            else:
                print(f"[ERROR] Backup file not found: {backup_filename}")
                return False
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            return False
    
    def list_backups(self):
        """List available backup files"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('videos_backup_')]
            backups.sort(reverse=True)
            return backups
        except Exception as e:
            print(f"[ERROR] Failed to list backups: {e}")
            return []
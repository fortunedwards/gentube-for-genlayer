import yt_dlp
import requests
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json

class VideoMetadataExtractor:
    """Extract metadata from various video platforms"""
    
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
    
    def extract(self, url):
        """Extract metadata from video URL"""
        platform = self.detect_platform(url)
        
        try:
            if platform in ['youtube', 'vimeo', 'dailymotion', 'twitch']:
                return self._extract_with_ytdlp(url, platform)
            elif platform == 'twitter':
                return self._extract_twitter(url)
            elif platform == 'linkedin':
                return self._extract_linkedin(url)
            else:
                return self._extract_generic(url)
        except Exception as e:
            return {
                'platform': platform,
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
    
    def _extract_with_ytdlp(self, url, platform):
        """Extract metadata using yt-dlp"""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'platform': platform,
                'title': info.get('title'),
                'description': info.get('description'),
                'duration': info.get('duration'),  # in seconds
                'duration_string': self._format_duration(info.get('duration')),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'upload_date': info.get('upload_date'),
                'uploader': info.get('uploader'),
                'uploader_id': info.get('uploader_id'),
                'thumbnail': info.get('thumbnail'),
                'thumbnails': info.get('thumbnails', [])[:3],  # First 3 thumbnails
                'tags': info.get('tags', []),
                'categories': info.get('categories', []),
                'webpage_url': info.get('webpage_url'),
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
    
    def _extract_twitter(self, url):
        """Extract metadata from Twitter/X videos"""
        # Basic Twitter metadata extraction
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            content = response.text
            
            # Extract basic info from meta tags
            title_match = re.search(r'<meta property="og:title" content="([^"]*)"', content)
            desc_match = re.search(r'<meta property="og:description" content="([^"]*)"', content)
            image_match = re.search(r'<meta property="og:image" content="([^"]*)"', content)
            
            return {
                'platform': 'twitter',
                'title': title_match.group(1) if title_match else None,
                'description': desc_match.group(1) if desc_match else None,
                'thumbnail': image_match.group(1) if image_match else None,
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'platform': 'twitter',
                'error': str(e),
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
    
    def _extract_linkedin(self, url):
        """Extract metadata from LinkedIn videos"""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            content = response.text
            
            title_match = re.search(r'<meta property="og:title" content="([^"]*)"', content)
            desc_match = re.search(r'<meta property="og:description" content="([^"]*)"', content)
            
            return {
                'platform': 'linkedin',
                'title': title_match.group(1) if title_match else None,
                'description': desc_match.group(1) if desc_match else None,
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'platform': 'linkedin',
                'error': str(e),
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
    
    def _extract_generic(self, url):
        """Generic metadata extraction for unknown platforms"""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            content = response.text
            
            # Extract Open Graph metadata
            og_data = {}
            og_patterns = {
                'title': r'<meta property="og:title" content="([^"]*)"',
                'description': r'<meta property="og:description" content="([^"]*)"',
                'image': r'<meta property="og:image" content="([^"]*)"',
                'video': r'<meta property="og:video" content="([^"]*)"',
                'url': r'<meta property="og:url" content="([^"]*)"'
            }
            
            for key, pattern in og_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    og_data[key] = match.group(1)
            
            # Extract basic HTML metadata
            title_match = re.search(r'<title>([^<]*)</title>', content, re.IGNORECASE)
            
            return {
                'platform': 'generic',
                'title': og_data.get('title') or (title_match.group(1) if title_match else None),
                'description': og_data.get('description'),
                'thumbnail': og_data.get('image'),
                'video_url': og_data.get('video'),
                'canonical_url': og_data.get('url'),
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'platform': 'generic',
                'error': str(e),
                'original_url': url,
                'extracted_at': datetime.now().isoformat()
            }
    
    def detect_platform(self, url):
        """Detect video platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        platform_patterns = {
            'youtube': ['youtube.com', 'youtu.be', 'm.youtube.com'],
            'vimeo': ['vimeo.com', 'player.vimeo.com'],
            'dailymotion': ['dailymotion.com', 'dai.ly'],
            'twitch': ['twitch.tv', 'clips.twitch.tv'],
            'twitter': ['twitter.com', 'x.com', 't.co'],
            'linkedin': ['linkedin.com'],
            'facebook': ['facebook.com', 'fb.watch'],
            'instagram': ['instagram.com'],
            'tiktok': ['tiktok.com'],
            'rumble': ['rumble.com'],
            'bitchute': ['bitchute.com'],
            'odysee': ['odysee.com'],
            'brighteon': ['brighteon.com']
        }
        
        for platform, domains in platform_patterns.items():
            if any(d in domain for d in domains):
                return platform
        
        return 'generic'
    
    def get_supported_platforms(self):
        """Get list of supported platforms"""
        return [
            {
                'name': 'YouTube',
                'domains': ['youtube.com', 'youtu.be'],
                'features': ['title', 'description', 'duration', 'thumbnails', 'view_count', 'tags']
            },
            {
                'name': 'Vimeo',
                'domains': ['vimeo.com'],
                'features': ['title', 'description', 'duration', 'thumbnails', 'view_count']
            },
            {
                'name': 'Dailymotion',
                'domains': ['dailymotion.com'],
                'features': ['title', 'description', 'duration', 'thumbnails', 'view_count']
            },
            {
                'name': 'Twitch',
                'domains': ['twitch.tv'],
                'features': ['title', 'description', 'duration', 'thumbnails', 'view_count']
            },
            {
                'name': 'Twitter/X',
                'domains': ['twitter.com', 'x.com'],
                'features': ['title', 'description', 'thumbnail']
            },
            {
                'name': 'LinkedIn',
                'domains': ['linkedin.com'],
                'features': ['title', 'description']
            },
            {
                'name': 'Facebook',
                'domains': ['facebook.com'],
                'features': ['title', 'description', 'thumbnail']
            },
            {
                'name': 'TikTok',
                'domains': ['tiktok.com'],
                'features': ['title', 'description', 'thumbnail']
            },
            {
                'name': 'Rumble',
                'domains': ['rumble.com'],
                'features': ['title', 'description', 'duration', 'thumbnails']
            },
            {
                'name': 'Generic',
                'domains': ['*'],
                'features': ['title', 'description', 'thumbnail']
            }
        ]
    
    def _format_duration(self, seconds):
        """Format duration from seconds to human readable string"""
        if not seconds:
            return None
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def validate_url(self, url):
        """Validate if URL is a supported video URL"""
        try:
            platform = self.detect_platform(url)
            return {
                'valid': True,
                'platform': platform,
                'supported': platform != 'generic'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
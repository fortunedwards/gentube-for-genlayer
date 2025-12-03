# Hybrid Interactive Video Archive

A two-part system combining a secure Flask admin dashboard with a fast static public archive.

## Architecture

- **Part A**: Admin Dashboard (Flask) - Secure backend for managing videos
- **Part B**: Public Archive (Static) - Fast frontend for browsing videos

## Setup Instructions

### 1. Admin Dashboard Setup

**Option A: Command Line**
```bash
cd admin_dashboard
pip install -r requirements.txt
python run.py
```

**Option B: Windows (Double-click)**
```
start_admin.bat
```

- Access at: http://localhost:5000
- Default login: `admin` / `admin123`
- Database and admin user created automatically

### 2. Public Archive Setup

**Option A: Command Line**
```bash
cd public_archive
python -m http.server 8000
```

**Option B: Windows (Double-click)**
```
start_public.bat
```

**Option C: Other servers**
```bash
npx serve .          # Node.js
php -S localhost:8000  # PHP
```

- Access at: http://localhost:8000
- Modern PWA with offline support, dark mode, and mobile-first design

## Usage Workflow

1. **Admin adds videos**: Log into Flask dashboard, add/edit videos
2. **Export data**: Click "Export Data" to generate `videos.json`
3. **Deploy**: Upload public_archive folder to static hosting
4. **Users browse**: Fast, searchable video archive

## Features

### Admin Dashboard
- Secure login system
- Add/edit/delete videos
- Export to JSON
- Video management interface

### Public Archive (Modern PWA)
- **Vue.js 3** reactive frontend
- **Progressive Web App** with offline support
- **Dark/Light mode** with system preference detection
- **Responsive design** mobile-first approach
- **YouTube/Vimeo embed** support with modal player
- **Infinite scroll** with lazy loading
- **Service Worker** caching for offline use
- **Install prompts** for mobile and desktop

## File Structure

```
GenTube/
├── admin_dashboard/          # Flask backend
│   ├── run.py               # Simple startup script
│   ├── app.py               # Main Flask app
│   ├── backup.py            # Database backup system
│   ├── bulk_operations.py   # Import/export operations
│   ├── forms.py             # WTForms validation
│   ├── video_metadata.py    # Video metadata extraction
│   ├── webhooks.py          # Auto-export webhooks
│   ├── templates/           # HTML templates
│   ├── requirements.txt     # Python dependencies
│   └── instance/videos.db   # SQLite database (auto-created)
├── public_archive/          # Modern PWA frontend
│   ├── index.html          # Vue.js application
│   ├── css/app.css         # Modern CSS with dark mode
│   ├── js/app.js           # Vue.js logic with PWA features
│   ├── manifest.json       # PWA manifest
│   ├── sw.js              # Service worker
│   └── videos.json        # Exported video data
├── start_admin.bat          # Windows: Start admin dashboard
├── start_public.bat         # Windows: Start public archive
└── README.md
```

## Deployment

### Admin Dashboard
- Deploy Flask app to Heroku, AWS, or any Python hosting
- Keep private/secure

### Public Archive
- Deploy to GitHub Pages, Netlify, or AWS S3
- Just upload the `public_archive` folder contents

## Security Notes

- Change the Flask SECRET_KEY in production
- Change default admin credentials
- Keep admin dashboard private
- Only the public archive should be publicly accessible
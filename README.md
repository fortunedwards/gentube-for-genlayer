# GenTube - Video Archive System for GenLayer

🎥 A modern video archive system with Netflix-style PWA frontend and secure Flask admin dashboard, specifically designed for GenLayer content.

## ✨ Features

### 🏠 Netflix-Style Home Page
- **Hero Section**: Featured YouTube videos with random rotation
- **Recently Added**: Grid of latest videos
- **Responsive Design**: Mobile-first approach
- **Dark/Light Mode**: System preference detection

### 🎯 Admin Dashboard
- **Modern UI**: Tailwind CSS with dark mode support
- **Video Management**: Add, edit, delete videos with metadata
- **Platform Support**: YouTube, Vimeo, Twitter/X detection
- **Bulk Import**: JSON file upload for multiple videos
- **Database Backups**: Automated backup system
- **Export System**: Generate videos.json for public archive

### 📱 Progressive Web App (PWA)
- **Vue.js 3**: Reactive frontend with smooth animations
- **Offline Support**: Service worker caching
- **Install Prompts**: Add to home screen capability
- **Video Player**: Embedded YouTube/Vimeo with fallbacks
- **Search & Filter**: Real-time video filtering
- **Infinite Scroll**: Lazy loading for performance

## 🚀 Quick Start

### Admin Dashboard
```bash
cd admin_dashboard
pip install -r requirements.txt
python run.py
```
- Access: http://localhost:5000

### Public Archive
```bash
cd public_archive
python -m http.server 8000
```
- Access: http://localhost:8000

### Windows Quick Start
- Double-click `start_admin.bat` for admin dashboard
- Double-click `start_public.bat` for public archive

## 🏗️ Architecture

```
GenTube/
├── admin_dashboard/         # Flask Backend
│   ├── templates/          # Modern Jinja2 templates
│   ├── static/            # Logo assets
│   ├── app.py             # Main Flask application
│   ├── forms.py           # WTForms validation
│   ├── backup.py          # Database backup system
│   └── requirements.txt   # Python dependencies
├── public_archive/         # Vue.js PWA Frontend
│   ├── index.html         # Netflix-style home page
│   ├── js/app.js          # Vue.js application logic
│   ├── manifest.json      # PWA configuration
│   ├── sw.js             # Service worker
│   └── videos.json       # Video data export
└── README.md
```

## 🎨 Design System

- **Colors**: Custom GenLayer brand colors with primary blue (#2A4D8E)
- **Typography**: Inter font family for modern look
- **Icons**: Material Symbols for consistency
- **Logos**: Conditional light/dark mode logos (logo1.png/logo2.png)
- **Responsive**: Mobile-first Tailwind CSS framework

## 🔧 Platform Support

| Platform | Embed Support | Preview | Notes |
|----------|---------------|---------|-------|
| YouTube | ✅ Full | ✅ Thumbnails | Featured in hero section |
| Vimeo | ✅ Full | ✅ Basic | Full embed support |
| Twitter/X | ❌ Link Only | 🅧 X Logo | Platform restrictions |
| Others | ❌ Link Only | 🎥 Generic | External links |

## 📊 Workflow

1. **Content Management**: Add videos via admin dashboard
2. **Auto-Export**: System generates videos.json automatically
3. **PWA Access**: Users browse via Netflix-style interface
4. **Deployment**: Static files deployable anywhere

## 🚀 Deployment

### Admin Dashboard
- **Heroku**: `git push heroku main`
- **AWS/DigitalOcean**: Python hosting
- **Keep Private**: Secure admin access only

### Public Archive
- **GitHub Pages**: Upload `public_archive/` contents
- **Netlify**: Drag & drop deployment
- **AWS S3**: Static website hosting
- **Vercel**: Connect GitHub repository

## 🔒 Security

- Change default admin credentials in production
- Update Flask SECRET_KEY for sessions
- Keep admin dashboard private/secured
- Public archive is safe for static hosting

## 🌟 GenLayer Integration

This system is specifically designed for GenLayer's video content needs:
- Curated GenLayer educational content
- Speaker-focused organization
- Platform-agnostic video management
- Modern, professional presentation

---

**Built by Fortune Edwards for the GenLayer Community** | Modern Video Archive System
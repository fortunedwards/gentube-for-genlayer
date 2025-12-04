# Single Vercel Deployment Guide

## 🚀 Deploy Both Components as One Project

### Structure
```
your-site.vercel.app/          # Public Archive (Vue.js PWA)
your-site.vercel.app/admin/    # Admin Dashboard (Flask API)
```

### Vercel Setup

1. **Import Repository**
   - Go to [vercel.com](https://vercel.com)
   - Import `fortunedwards/gentube-for-genlayer`
   - **Root Directory**: `/` (default)
   - **Framework**: Other

2. **Environment Variables** (Required)
   ```
   SECRET_KEY=your-random-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   DATABASE_URL=sqlite:///tmp/videos.db
   FLASK_ENV=production
   ```

3. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

### URLs After Deployment
- **Public Site**: `https://your-project.vercel.app`
- **Admin Dashboard**: `https://your-project.vercel.app/admin`

### How It Works
- **Static Files**: Public archive served directly
- **Admin Routes**: `/admin/*` routes to Flask serverless function
- **Database**: SQLite in `/tmp` (resets on deployment)
- **Data Export**: Admin exports to `public_archive/videos.json`

### Workflow
1. Access admin at `/admin`
2. Add/manage videos
3. Export data (updates public site automatically)
4. Users browse public site at root URL

This gives you one URL for everything!
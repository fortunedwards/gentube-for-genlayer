# Separate Admin Deployment Guide

## 🚀 Deploy Admin Dashboard Separately

### Step 1: Create New Vercel Project for Admin

1. **Go to Vercel Dashboard**
   - Create new project
   - Import `fortunedwards/gentube-for-genlayer`
   - **Project Name**: `gentube-admin`
   - **Root Directory**: `admin_dashboard`
   - **Framework**: Other

2. **Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=secure-password
   DATABASE_URL=sqlite:///tmp/videos.db
   FLASK_ENV=production
   ```

### Step 2: Connect to Public Site

Your URLs will be:
- **Public Site**: `https://gentube-for-genlayer.vercel.app/`
- **Admin Dashboard**: `https://gentube-admin.vercel.app/`

### Step 3: Update Public Site with Admin Data

**Option A: Manual Update**
1. Login to admin dashboard
2. Add/edit videos
3. Go to `/api/videos` endpoint
4. Copy the JSON response
5. Update `public_archive/videos.json` in GitHub
6. Public site auto-updates

**Option B: API Integration** (Recommended)
Update your public site to fetch from admin API:

```javascript
// In public_archive/js/app.js
const ADMIN_API = 'https://gentube-admin.vercel.app/api/videos';

async function loadVideos() {
    try {
        const response = await fetch(ADMIN_API);
        const videos = await response.json();
        return videos;
    } catch (error) {
        // Fallback to local videos.json
        const response = await fetch('./videos.json');
        return await response.json();
    }
}
```

### Benefits of Separate Deployment:
- ✅ Full Flask functionality
- ✅ Persistent database (with external DB)
- ✅ Better performance
- ✅ Independent scaling
- ✅ Easier debugging

### Next Steps:
1. Deploy admin as separate Vercel project
2. Test admin functionality
3. Set up API connection to public site
4. Consider external database for persistence
# GenTube Deployment Guide

## 🚀 GitHub + Vercel Deployment

### Step 1: GitHub Setup

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/gentube.git
   git push -u origin main
   ```

2. **Repository Structure**
   ```
   gentube/
   ├── admin_dashboard/     # Flask Admin (Separate Vercel project)
   ├── public_archive/      # Vue.js PWA (Main Vercel project)
   └── README.md
   ```

### Step 2: Deploy Public Archive (Main Site)

1. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - **Root Directory**: Leave as default (/)
   - **Build Settings**: Use existing `vercel.json`

2. **Environment Variables** (None needed for public archive)

3. **Custom Domain** (Optional)
   - Add your domain in Vercel dashboard
   - Update DNS records as instructed

### Step 3: Deploy Admin Dashboard (Separate Project)

1. **Create New Vercel Project**
   - Import same GitHub repository
   - **Root Directory**: Set to `admin_dashboard`
   - **Framework**: Other
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

2. **Environment Variables** (Required)
   ```
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=your-admin-username
   ADMIN_PASSWORD=your-secure-password
   DATABASE_URL=sqlite:///tmp/videos.db
   FLASK_ENV=production
   ```

3. **Important Notes**
   - Admin dashboard will use temporary SQLite database
   - Database resets on each deployment (Vercel limitation)
   - Consider using external database for production

### Step 4: Workflow

1. **Content Management**
   - Access admin at: `https://your-admin.vercel.app`
   - Add/edit videos through dashboard
   - Export data to update public archive

2. **Data Sync**
   - Manual: Use "Export Data" button in admin
   - Automatic: Set up GitHub Actions (optional)

3. **Public Access**
   - Users visit: `https://your-site.vercel.app`
   - PWA features work automatically

## 🔧 Alternative: Database Solutions

### Option 1: PostgreSQL (Recommended)
```bash
# Add to admin requirements.txt
psycopg2-binary==2.9.7

# Environment variable
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Option 2: MongoDB Atlas
```bash
# Add to admin requirements.txt
pymongo==4.5.0
flask-pymongo==2.3.0

# Update app.py for MongoDB
```

### Option 3: Supabase
```bash
# Add to admin requirements.txt
supabase==1.0.4

# Environment variable
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## 🚀 Quick Deploy Commands

### Deploy Public Archive
```bash
# Already configured with vercel.json
# Just push to GitHub and Vercel auto-deploys
git add .
git commit -m "Update public archive"
git push
```

### Deploy Admin Dashboard
```bash
# Push changes
git add admin_dashboard/
git commit -m "Update admin dashboard"
git push

# Vercel auto-deploys from admin_dashboard/ folder
```

## 🔒 Security Checklist

- [ ] Change default admin credentials
- [ ] Set strong SECRET_KEY
- [ ] Use HTTPS (Vercel provides automatically)
- [ ] Keep admin URL private
- [ ] Set up proper CORS if needed
- [ ] Use environment variables for secrets

## 📱 PWA Features

The public archive automatically includes:
- ✅ Service Worker caching
- ✅ Offline functionality
- ✅ Install prompts
- ✅ App-like experience
- ✅ Mobile responsive design

## 🎯 URLs After Deployment

- **Public Archive**: `https://your-repo-name.vercel.app`
- **Admin Dashboard**: `https://your-admin-project.vercel.app`
- **GitHub Repository**: `https://github.com/username/gentube`

---

**Ready to deploy!** Follow the steps above and your GenTube system will be live on Vercel with GitHub integration.
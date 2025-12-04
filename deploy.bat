@echo off
echo GenTube Deployment Helper
echo ========================

echo.
echo 1. Initialize Git Repository
git init
git add .
git commit -m "Initial GenTube deployment"

echo.
echo 2. Next Steps:
echo    - Create GitHub repository at: https://github.com/new
echo    - Run: git remote add origin https://github.com/USERNAME/REPO.git
echo    - Run: git push -u origin main
echo    - Go to vercel.com and import your repository
echo    - Deploy public archive (root directory)
echo    - Deploy admin dashboard (admin_dashboard directory)

echo.
echo 3. Don't forget to set environment variables in Vercel:
echo    SECRET_KEY=your-secret-key
echo    ADMIN_USERNAME=your-username  
echo    ADMIN_PASSWORD=your-password

pause
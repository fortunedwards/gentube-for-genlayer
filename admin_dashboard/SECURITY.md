# Security Features

## Overview
The GenTube admin dashboard now includes enhanced security features:

## Features Implemented

### 1. JWT Authentication
- Replaces session-based authentication
- 24-hour token expiration
- HTTP-only secure cookies
- Automatic token refresh

### 2. Password Security
- bcrypt hashing (cost factor 12)
- Secure password storage
- Protection against rainbow table attacks

### 3. Rate Limiting
- Login attempts: 5 per minute
- Global limits: 200/day, 50/hour
- IP-based tracking
- Prevents brute force attacks

### 4. Environment Variables
- Sensitive data moved to `.env` file
- No hardcoded secrets in source code
- Easy configuration management

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your secure values
   ```

3. Run setup script:
   ```bash
   python setup.py
   ```

4. Start application:
   ```bash
   python app.py
   ```

## Production Deployment

### Required Changes
1. **Change default credentials**:
   ```
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_secure_password
   ```

2. **Generate secure keys**:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))  # For SECRET_KEY
   print(secrets.token_urlsafe(32))  # For JWT_SECRET_KEY
   ```

3. **Use HTTPS**: Enable SSL/TLS in production

4. **Database**: Consider PostgreSQL for production

### Security Headers
Add these headers in production:
- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`

## Rate Limits
- Login endpoint: 5 attempts per minute
- All endpoints: 200 requests per day, 50 per hour
- Customize in `app.py` if needed

## Token Management
- Tokens expire after 24 hours
- Stored in HTTP-only cookies
- Automatically cleared on logout
- No client-side token storage

## Password Policy
Current implementation uses bcrypt with default cost factor.
Consider implementing:
- Minimum password length
- Password complexity requirements
- Password history
- Account lockout after failed attempts
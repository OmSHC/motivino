# Google OAuth2 Setup Guide

This guide will help you set up Google OAuth2 authentication for the Interactive Student Motivation News Website.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API

## Step 2: Configure OAuth Consent Screen

1. In the Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace)
3. Fill in the required information:
   - **App name**: Student Motivation News
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Add scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
5. Add test users (your email and any test accounts)

## Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://127.0.0.1:8000/api/auth/oauth2/google/callback/`
   - `http://localhost:8000/api/auth/oauth2/google/callback/`
   - `http://127.0.0.1:3000/auth/callback` (for React frontend)
   - `http://localhost:3000/auth/callback` (for React frontend)
5. Copy the Client ID and Client Secret

## Step 4: Update Environment Variables

Add these to your `.env` file:

```bash
# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# OAuth2 Settings
OAUTH2_REDIRECT_URI=http://127.0.0.1:8000/api/auth/oauth2/google/callback/
```

## Step 5: Test the Setup

1. Start your Django server: `python manage.py runserver`
2. Visit: `http://127.0.0.1:8000/api/auth/oauth2/google/`
3. You should be redirected to Google's OAuth consent screen
4. After authorization, you'll be redirected back to your app

## Step 6: Frontend Integration

The React frontend is already configured to work with the OAuth2 flow. The authentication will be handled through the Django backend.

## Troubleshooting

### Common Issues:

1. **"redirect_uri_mismatch"**: Make sure the redirect URI in Google Console matches exactly
2. **"access_denied"**: Check that the OAuth consent screen is properly configured
3. **"invalid_client"**: Verify your Client ID and Secret are correct

### Development vs Production:

- For development: Use `http://127.0.0.1:8000` and `http://localhost:8000`
- For production: Update redirect URIs to your production domain
- Update `ALLOWED_HOSTS` in Django settings for production

## Security Notes:

- Never commit your Client Secret to version control
- Use environment variables for all sensitive configuration
- Enable HTTPS in production
- Regularly rotate your OAuth2 credentials

# Gmail Authentication Setup Guide

This guide will help you set up Gmail (Google) authentication for the Interactive Student Motivation News Website.

## 🚀 Quick Setup

### Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable Required APIs**
   - Go to "APIs & Services" > "Library"
   - Enable "Google+ API" and "Google OAuth2 API"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type (unless you have Google Workspace)
   - Fill in the required information:
     - **App name**: Student Motivation News
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Add scopes:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
   - Add test users (your email and any test accounts)

4. **Create OAuth2 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://127.0.0.1:3000/auth/callback`
     - `http://localhost:3000/auth/callback`
     - `http://127.0.0.1:8000/api/users/oauth/google/callback/`
   - Copy the Client ID and Client Secret

### Step 2: Environment Configuration

1. **Copy the environment file:**
```bash
cp env.example .env
```

2. **Edit the `.env` file with your credentials:**
```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-actual-client-id-here
GOOGLE_CLIENT_SECRET=your-actual-client-secret-here
GOOGLE_REDIRECT_URI=http://127.0.0.1:3000/auth/callback
```

### Step 3: Test the Setup

1. **Start the Django server:**
```bash
source venv/bin/activate
python manage.py runserver
```

2. **Start the React frontend:**
```bash
cd frontend
npm start
```

3. **Test Gmail authentication:**
   - Visit: http://localhost:3000
   - Click "Continue with Google"
   - Complete the OAuth flow

## 🔧 How It Works

### Authentication Flow

1. **User clicks "Sign in with Google"**
2. **Frontend requests OAuth URL from backend**
3. **User is redirected to Google OAuth consent screen**
4. **User authorizes the application**
5. **Google redirects back with authorization code**
6. **Backend exchanges code for access token**
7. **Backend fetches user info from Google**
8. **User is created/logged in and redirected to app**

### API Endpoints

- `GET /api/users/oauth/google/url/` - Get Google OAuth authorization URL
- `POST /api/users/oauth/google/callback/` - Handle OAuth callback with code

### Frontend Components

- `GmailAuth` - Main authentication component with Google sign-in buttons
- `AuthCallback` - Handles OAuth redirect and token processing

## 🛠️ Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch"**
   - **Solution**: Make sure the redirect URI in Google Console exactly matches your `.env` file
   - Check: `GOOGLE_REDIRECT_URI=http://127.0.0.1:3000/auth/callback`

2. **"access_denied"**
   - **Solution**: Check that the OAuth consent screen is properly configured
   - Make sure test users are added if in testing mode

3. **"invalid_client"**
   - **Solution**: Verify your Client ID and Secret are correct in `.env`
   - Check for extra spaces or characters

4. **"scope" errors**
   - **Solution**: Ensure the required scopes are added in OAuth consent screen
   - Required: `email`, `profile`, `openid`

### Development vs Production

**Development:**
- Use `http://127.0.0.1:3000/auth/callback`
- Add your email as a test user
- Use "External" user type

**Production:**
- Update redirect URIs to your production domain
- Complete OAuth consent screen verification
- Update `ALLOWED_HOSTS` in Django settings
- Use HTTPS for all URLs

## 🔒 Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables for all sensitive data**
3. **Enable HTTPS in production**
4. **Regularly rotate OAuth2 credentials**
5. **Monitor OAuth usage in Google Cloud Console**
6. **Use least privilege scopes**

## 📱 Mobile Considerations

For mobile app integration:
- Add mobile redirect URIs to Google Console
- Use deep links for mobile OAuth flow
- Consider using Google Sign-In SDK for native apps

## 🎯 Testing

### Manual Testing
1. Test with different Google accounts
2. Test popup vs redirect flows
3. Test error scenarios (denied access, network errors)
4. Test token refresh and expiration

### Automated Testing
```bash
# Run the test suite
python run_tests.py

# Test OAuth endpoints specifically
python manage.py test apps.users.tests.UserAuthenticationTest
```

## 📚 Additional Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/)
- [React OAuth Best Practices](https://auth0.com/blog/complete-guide-to-react-user-authentication/)

## 🆘 Support

If you encounter issues:
1. Check the Django logs: `tail -f logs/django.log`
2. Check browser console for frontend errors
3. Verify Google Cloud Console configuration
4. Test with a fresh OAuth consent screen setup

---

**🎉 Once configured, users can sign in with their Gmail accounts and access personalized motivational content!**



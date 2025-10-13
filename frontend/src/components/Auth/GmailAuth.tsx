import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import { User } from '../../types';

interface GmailAuthProps {
  onAuthSuccess: (user: User, token: string) => void;
  onAuthError: (error: string) => void;
}

const GmailAuth: React.FC<GmailAuthProps> = ({ onAuthSuccess, onAuthError }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [authUrl, setAuthUrl] = useState<string>('');

  const fetchAuthUrl = async () => {
    try {
      const response = await apiService.getGoogleAuthUrl();
      setAuthUrl(response.data.auth_url);
    } catch (error) {
      console.error('Failed to get auth URL:', error);
      onAuthError('Failed to initialize Google authentication');
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.demoLogin({
        email: 'demo@example.com',
        first_name: 'Demo',
        last_name: 'Student'
      });
      
      if (response.data.access_token) {
        onAuthSuccess(response.data.user, response.data.access_token);
      }
    } catch (error) {
      console.error('Demo login failed:', error);
      onAuthError('Demo login failed');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Get the Google OAuth URL when component mounts
    fetchAuthUrl();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleGoogleSignIn = () => {
    if (authUrl) {
      // Open Google OAuth in a popup window
      const popup = window.open(
        authUrl,
        'google-auth',
        'width=500,height=600,scrollbars=yes,resizable=yes'
      );

      // Listen for the popup to close or receive a message
      const checkClosed = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkClosed);
          setIsLoading(false);
        }
      }, 1000);

      // Listen for messages from the popup
      const messageListener = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        
        if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
          const { user, access_token } = event.data;
          onAuthSuccess(user, access_token);
          popup?.close();
          clearInterval(checkClosed);
          window.removeEventListener('message', messageListener);
        } else if (event.data.type === 'GOOGLE_AUTH_ERROR') {
          onAuthError(event.data.error);
          popup?.close();
          clearInterval(checkClosed);
          window.removeEventListener('message', messageListener);
        }
      };

      window.addEventListener('message', messageListener);
      setIsLoading(true);
    }
  };

  const handleDirectRedirect = () => {
    if (authUrl) {
      window.location.href = authUrl;
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Sign in with Gmail
        </h2>
        <p className="text-gray-600 mb-6">
          Use your Gmail account to access personalized motivational content
        </p>
      </div>

      <div className="space-y-3">
        <button
          onClick={handleGoogleSignIn}
          disabled={isLoading || !authUrl}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600 mr-3"></div>
              Connecting...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google (Popup)
            </>
          )}
        </button>

        <button
          onClick={handleDirectRedirect}
          disabled={isLoading || !authUrl}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Continue with Google (Redirect)
        </button>

        <button
          onClick={handleDemoLogin}
          disabled={isLoading}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-gray-100 text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600 mr-3"></div>
              Signing in...
            </>
          ) : (
            <>
              <span className="text-2xl mr-3">🎓</span>
              Demo Login (No Google Setup Required)
            </>
          )}
        </button>
      </div>

      <div className="text-center">
        <p className="text-sm text-gray-500">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Demo mode: Use demo login to test the application without Google OAuth setup
        </p>
      </div>

      {/* Admin Login Link */}
      <div className="mt-6 pt-6 border-t border-gray-200 text-center">
        <button
          onClick={async () => {
            setIsLoading(true);
            try {
              const response = await apiService.demoLogin({
                email: 'admin@example.com',
                first_name: 'Admin',
                last_name: 'User'
              });
              
              if (response.data.access_token) {
                onAuthSuccess(response.data.user, response.data.access_token);
              }
            } catch (error) {
              console.error('Admin login failed:', error);
              onAuthError('Admin login failed');
            } finally {
              setIsLoading(false);
            }
          }}
          disabled={isLoading}
          className="text-sm text-gray-600 hover:text-red-600 font-medium transition-colors duration-200"
        >
          👨‍💼 Admin Access
        </button>
      </div>
    </div>
  );
};

export default GmailAuth;

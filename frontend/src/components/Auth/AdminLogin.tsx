import React, { useState } from 'react';
import { apiService } from '../../services/api';
import { User } from '../../types';

interface AdminLoginProps {
  onAuthSuccess: (user: User, token: string) => void;
  onAuthError: (error: string) => void;
  onBackToStudent: () => void;
}

const AdminLogin: React.FC<AdminLoginProps> = ({ onAuthSuccess, onAuthError, onBackToStudent }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleAdminLogin = async () => {
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
  };

  return (
    <div className="space-y-4">
      <div className="text-center">
        <div className="text-6xl mb-4">👨‍💼</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Admin Access
        </h2>
        <p className="text-gray-600 mb-6">
          Sign in as administrator to manage content
        </p>
      </div>

      <div className="space-y-3">
        <button
          onClick={handleAdminLogin}
          disabled={isLoading}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              Signing in as Admin...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Sign in as Admin
            </>
          )}
        </button>

        <button
          onClick={onBackToStudent}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
        >
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Student Login
        </button>
      </div>

      <div className="text-center">
        <p className="text-sm text-gray-500">
          Admin access is required to create and manage content
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Demo admin: admin@example.com
        </p>
      </div>
    </div>
  );
};

export default AdminLogin;

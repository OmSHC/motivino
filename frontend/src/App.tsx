import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import QuotationBanner from './components/Layout/QuotationBanner';
import UserProfileModal from './components/Layout/UserProfileModal';
import ContentFeed from './components/Content/ContentFeed';
import ContentDetail from './components/Content/ContentDetail';
import LoginForm from './components/Auth/LoginForm';
import SignupForm from './components/Auth/SignupForm';
import AuthCallback from './components/Auth/AuthCallback';
import AdminDashboard from './components/Admin/AdminDashboard';
import { User } from './types';
import { apiService } from './services/api';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const response = await apiService.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem('access_token');
    } finally {
      setLoading(false);
    }
  };

  const handleUserUpdate = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const handleAuthSuccess = (user: User, token: string, sessionKey?: string) => {
    setUser(user);
    localStorage.setItem('access_token', token);
    if (sessionKey) {
      localStorage.setItem('session_key', sessionKey);
    }
  };

  const handleAuthError = (error: string) => {
    console.error('Authentication error:', error);
    // You could show a toast notification here
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="card">
            {authMode === 'login' ? (
              <LoginForm
                onAuthSuccess={handleAuthSuccess}
                onSwitchToSignup={() => setAuthMode('signup')}
              />
            ) : (
              <SignupForm
                onAuthSuccess={handleAuthSuccess}
                onSwitchToLogin={() => setAuthMode('login')}
              />
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
        {/* Quotation Banner - Full Width */}
        <QuotationBanner className="w-full" />

        <div className="flex">
          <Sidebar user={user} onProfileClick={() => setShowProfileModal(true)} />

          <main className="flex-1 min-h-screen overflow-auto lg:ml-64">
            <div className="p-6">
              <Routes>
                <Route path="/" element={<ContentFeed contentType="MIXED" user={user} />} />
                <Route path="/news" element={<ContentFeed contentType="MOTIVATION" user={user} />} />
                <Route path="/jokes" element={<ContentFeed contentType="JOKES" user={user} />} />
                <Route path="/quotations" element={<ContentFeed contentType="QUOTATION" user={user} />} />
                <Route path="/stories" element={<ContentFeed contentType="PUZZLE" user={user} />} />
                <Route path="/tongue-twister" element={<ContentFeed contentType="TONGUE_TWISTER" user={user} />} />
                <Route path="/saved" element={<ContentFeed contentType="SAVED" user={user} />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/create-story" element={<AdminDashboard user={user} />} />
                <Route path="/admin" element={<Navigate to="/admin/" replace />} />
                {/* Individual content pages */}
                <Route path="/content/:id" element={<ContentDetail />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </main>
        </div>

        <UserProfileModal
          user={user}
          isOpen={showProfileModal}
          onClose={() => setShowProfileModal(false)}
          onUserUpdate={handleUserUpdate}
        />
      </div>
    </Router>
  );
}

export default App;
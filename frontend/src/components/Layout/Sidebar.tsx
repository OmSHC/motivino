import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  NewspaperIcon,
  FaceSmileIcon,
  ChatBubbleLeftRightIcon,
  BookOpenIcon,
  BookmarkIcon,
  CogIcon,
  UserCircleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { User } from '../../types';
import { apiService } from '../../services/api';

interface SidebarProps {
  user: User | null;
  onProfileClick: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ user, onProfileClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const menuItems = [
    { name: 'Inspire', path: '/', icon: HomeIcon },
    { name: 'Quotations', path: '/quotations', icon: ChatBubbleLeftRightIcon },
    { name: 'Puzzles', path: '/stories', icon: BookOpenIcon },
    { name: 'Jokes', path: '/jokes', icon: FaceSmileIcon },
    { name: 'Tongue Twister', path: '/tongue-twister', icon: ChatBubbleLeftRightIcon },
    { name: 'Saved', path: '/saved', icon: BookmarkIcon },
  ];

  const isAdmin = user?.role === 'ADMIN';

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-[60]">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-md bg-white shadow-lg"
        >
          {isOpen ? (
            <XMarkIcon className="h-6 w-6 text-gray-600" />
          ) : (
            <Bars3Icon className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="flex flex-col h-screen">

          {/* Navigation */}
          <nav className="px-4 py-6 space-y-2 overflow-y-auto">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200
                    ${isActive 
                      ? 'bg-primary-100 text-primary-700 border-r-4 border-primary-600' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}

            {/* Create Story - For ADMIN users only */}
            {isAdmin && (
              <>
                <div className="border-t border-gray-200 my-4"></div>
                <Link
                  to="/create-story"
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200
                    ${location.pathname === '/create-story' 
                      ? 'bg-green-100 text-green-700 border-r-4 border-green-600' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }
                  `}
                >
                  <CogIcon className="h-5 w-5" />
                  <span className="font-medium">📝 My Submission</span>
                </Link>
              </>
            )}
          </nav>

          {/* User profile - Fixed at bottom */}
          {user && (
            <div className="mt-auto p-4 border-t border-gray-200 bg-white">
              <button
                onClick={onProfileClick}
                className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 transition-colors duration-200 mb-2"
              >
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-sm">
                    {user.initials}
                  </span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                  <p className="text-xs text-primary-600">
                    {user.visit_days_count} days visited
                  </p>
                </div>
                <UserCircleIcon className="h-5 w-5 text-gray-400" />
              </button>

              <button
                onClick={async () => {
                  await apiService.logout();
                  localStorage.removeItem('access_token');
                  window.location.href = '/';
                }}
                className="w-full flex items-center space-x-3 p-3 rounded-lg text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                </svg>
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-[55] lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;

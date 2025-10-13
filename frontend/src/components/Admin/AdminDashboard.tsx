import React, { useState } from 'react';
import { User } from '../../types';
import ContentCreationForm from './ContentCreationForm';
import ContentManagement from './ContentManagement';
import UserStorySubmission from './UserStorySubmission';
import PendingApprovals from './PendingApprovals';

interface AdminDashboardProps {
  user: User;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user }) => {
  const isAdmin = user.role === 'ADMIN';
  const [activeTab, setActiveTab] = useState<'create' | 'manage' | 'pending' | 'my-stories'>('create');

  return (
    <div className="max-w-7xl mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {isAdmin ? 'Admin Dashboard' : 'Create Your Story'}
        </h1>
        <p className="text-gray-600">
          {isAdmin 
            ? `Welcome, ${user.first_name}! Create and manage motivational content for students.`
            : `Share your inspiring story with fellow students, ${user.first_name}!`
          }
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('create')}
            className={`
              py-4 px-1 border-b-2 font-medium text-sm
              ${activeTab === 'create'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            {isAdmin ? 'Create Content' : '✨ Submit Story'}
          </button>
          
          {!isAdmin && (
            <button
              onClick={() => setActiveTab('my-stories')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'my-stories'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              📝 My Submissions
            </button>
          )}
          
          {isAdmin && (
            <>
              <button
                onClick={() => setActiveTab('pending')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'pending'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                🔔 Pending Approvals
              </button>
              <button
                onClick={() => setActiveTab('manage')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'manage'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                Manage Content
              </button>
            </>
          )}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'create' && (
          isAdmin ? <ContentCreationForm /> : <UserStorySubmission user={user} />
        )}
        {activeTab === 'my-stories' && !isAdmin && <UserStorySubmission user={user} showMySubmissions={true} />}
        {activeTab === 'pending' && isAdmin && <PendingApprovals />}
        {activeTab === 'manage' && isAdmin && <ContentManagement />}
      </div>
    </div>
  );
};

export default AdminDashboard;

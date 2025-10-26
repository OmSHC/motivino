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
  const [activeTab, setActiveTab] = useState<'approved' | 'pending' | 'rejected' | 'manage' | 'admin-pending' | 'admin-manage'>(
    isAdmin ? 'admin-pending' : 'approved'
  );

  // Check if we're on the my-submissions route
  const isMySubmissionsRoute = window.location.pathname === '/my-submissions';

  return (
    <div className="max-w-7xl mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {isMySubmissionsRoute ? 'My Submissions' : (isAdmin ? 'Admin Dashboard' : 'Create Your Story')}
        </h1>
        <p className="text-gray-600">
          {isMySubmissionsRoute 
            ? `View and manage your submitted content, ${user.first_name}!`
            : isAdmin 
            ? `Welcome, ${user.first_name}! Create and manage motivational content for students.`
            : `Share your inspiring story with fellow students, ${user.first_name}!`
          }
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {/* Show user submission tabs for my-submissions route or non-admin users */}
          {(isMySubmissionsRoute || !isAdmin) && (
            <>
              <button
                onClick={() => setActiveTab('approved')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'approved'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                ✅ Approved
              </button>
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
                ⏳ Pending
              </button>
              <button
                onClick={() => setActiveTab('rejected')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'rejected'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                ❌ Rejected
              </button>
            </>
          )}
          
          {/* Show admin tabs only for admin users on create-story route */}
          {isAdmin && !isMySubmissionsRoute && (
            <>
              <button
                onClick={() => setActiveTab('admin-pending')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'admin-pending'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                🔔 Pending Approvals
              </button>
              <button
                onClick={() => setActiveTab('admin-manage')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === 'admin-manage'
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
        {/* Show user submission content for my-submissions route or non-admin users */}
        {(isMySubmissionsRoute || !isAdmin) && (
          <>
            {activeTab === 'approved' && <UserStorySubmission user={user} showMySubmissions={true} statusFilter="approved" />}
            {activeTab === 'pending' && <UserStorySubmission user={user} showMySubmissions={true} statusFilter="pending" />}
            {activeTab === 'rejected' && <UserStorySubmission user={user} showMySubmissions={true} statusFilter="rejected" />}
          </>
        )}
        
        {/* Show admin content only for admin users on create-story route */}
        {isAdmin && !isMySubmissionsRoute && (
          <>
            {activeTab === 'admin-pending' && <PendingApprovals />}
            {activeTab === 'admin-manage' && <ContentManagement />}
          </>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;

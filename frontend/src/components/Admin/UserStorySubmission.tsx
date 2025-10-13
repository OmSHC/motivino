import React, { useState, useEffect } from 'react';
import { User, Content } from '../../types';
import { apiService } from '../../services/api';
import MDEditor from '@uiw/react-md-editor';

interface UserStorySubmissionProps {
  user: User;
  showMySubmissions?: boolean;
}

const UserStorySubmission: React.FC<UserStorySubmissionProps> = ({ user, showMySubmissions = false }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('MOTIVATION');
  const [targetGrade, setTargetGrade] = useState<number | null>(null);
  const [targetSchool, setTargetSchool] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [mySubmissions, setMySubmissions] = useState<Content[]>([]);
  const [editingSubmission, setEditingSubmission] = useState<Content | null>(null);

  useEffect(() => {
    if (showMySubmissions) {
      loadMySubmissions();
    }
  }, [showMySubmissions]);

  const loadMySubmissions = async () => {
    try {
      const response = await apiService.getMySubmissions();
      setMySubmissions(response.data);
    } catch (err) {
      console.error('Failed to load submissions:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (editingSubmission) {
        await apiService.resubmit(editingSubmission.id, {
          title,
          rich_content: content,
          content_type: contentType,
          target_grade: targetGrade,
          target_school: targetSchool,
          youtube_url: youtubeUrl
        });
        setSuccess('Story resubmitted successfully! It will be reviewed again.');
      } else {
        await apiService.submitStory({
          title,
          rich_content: content,
          content_type: contentType,
          target_grade: targetGrade,
          target_school: targetSchool,
          youtube_url: youtubeUrl
        });
        setSuccess('Story submitted successfully! It will be reviewed before publishing.');
      }

      // Reset form
      setTitle('');
      setContent('');
      setContentType('MOTIVATION');
      setTargetGrade(null);
      setTargetSchool('');
      setYoutubeUrl('');
      setEditingSubmission(null);

      // Refresh submissions list
      if (showMySubmissions) {
        await loadMySubmissions();
      }
    } catch (err) {
      setError('Failed to submit story. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (submission: Content) => {
    setEditingSubmission(submission);
    setTitle(submission.title || '');
    setContent(submission.rich_content || submission.body);
    setContentType(submission.content_type);
    setTargetGrade(submission.target_grade || null);
    setTargetSchool(submission.target_school || '');
    setYoutubeUrl(submission.youtube_url || '');
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            ⏳ Pending Review
          </span>
        );
      case 'approved':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            ✅ Approved
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            ❌ Rejected
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Submission Form */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">
          {editingSubmission ? '✏️ Edit Submission' : '✨ Submit Your Story'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter a title for your story..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content Type
              </label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="MOTIVATION">💪 Motivation</option>
                <option value="JOKES">😄 Jokes</option>
                <option value="QUOTATION">💭 Quotation</option>
                <option value="PUZZLE">🧩 Puzzle</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Grade
              </label>
              <select
                value={targetGrade?.toString() || ''}
                onChange={(e) => setTargetGrade(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Grades</option>
                {Array.from({ length: 12 }, (_, i) => i + 1).map(grade => (
                  <option key={grade} value={grade}>Grade {grade}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target School (Optional)
            </label>
            <input
              type="text"
              value={targetSchool}
              onChange={(e) => setTargetSchool(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter school name..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content
            </label>
            <MDEditor
              value={content}
              onChange={(val) => setContent(val || '')}
              preview="edit"
              height={300}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              YouTube Video URL (optional)
            </label>
            <input
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>

          {error && (
            <div className="text-red-600 bg-red-50 p-3 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="text-green-600 bg-green-50 p-3 rounded-lg">
              {success}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Submitting...' : editingSubmission ? 'Resubmit Story' : 'Submit Story'}
            </button>
            
            {editingSubmission && (
              <button
                type="button"
                onClick={() => {
                  setEditingSubmission(null);
                  setTitle('');
                  setContent('');
                  setYoutubeUrl('');
                }}
                className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel Edit
              </button>
            )}
          </div>
        </form>
      </div>

      {/* My Submissions List */}
      {showMySubmissions && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">
            📝 My Submissions
          </h2>

          <div className="space-y-4">
            {mySubmissions.map((submission) => (
              <div
                key={submission.id}
                className="border rounded-lg p-4 hover:border-primary-500 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium">
                      {submission.title || 'Untitled Story'}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Submitted on {new Date(submission.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {getStatusBadge(submission.approval_status)}
                </div>

                {submission.rejection_reason && (
                  <div className="mt-3 text-sm bg-red-50 text-red-700 p-3 rounded-lg">
                    <strong>Rejection Reason:</strong> {submission.rejection_reason}
                  </div>
                )}

                {submission.approval_status === 'rejected' && (
                  <button
                    onClick={() => handleEdit(submission)}
                    className="mt-3 text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    ✏️ Edit and Resubmit
                  </button>
                )}
              </div>
            ))}

            {mySubmissions.length === 0 && (
              <p className="text-center text-gray-500 py-8">
                You haven't submitted any stories yet.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserStorySubmission;
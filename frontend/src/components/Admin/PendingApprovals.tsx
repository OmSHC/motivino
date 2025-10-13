import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import { Content } from '../../types';
import { Dialog, DialogBackdrop, DialogTitle } from '@headlessui/react';

const PendingApprovals: React.FC = () => {
  const [pendingContent, setPendingContent] = useState<Content[]>([]);
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRejectionDialog, setShowRejectionDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    loadPendingContent();
  }, []);

  const loadPendingContent = async () => {
    try {
      const response = await apiService.getPendingSubmissions();
      console.log('Pending submissions loaded:', response.data);
      setPendingContent(response.data);
    } catch (err) {
      setError('Failed to load pending submissions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (contentId: string) => {
    try {
      await apiService.approveSubmission(contentId);
      await loadPendingContent();
      setSelectedContent(null);
      setError(null);
    } catch (err) {
      setError('Failed to approve content');
      console.error(err);
    }
  };

  const handleRejectClick = () => {
    if (!selectedContent) return;
    setShowRejectionDialog(true);
  };

  const handleReject = async () => {
    if (!selectedContent || !rejectionReason.trim()) {
      setError('Please provide a reason for rejection');
      return;
    }

    try {
      await apiService.rejectSubmission(selectedContent.id, rejectionReason);
      setShowRejectionDialog(false);
      setRejectionReason('');
      await loadPendingContent();
      setSelectedContent(null);
      setError(null);
    } catch (err) {
      setError('Failed to reject content');
      console.error(err);
    }
  };

  const extractYouTubeId = (url: string): string | null => {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 p-4 rounded-lg bg-red-50">
        {error}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel - List of Pending Stories */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h2 className="text-lg font-semibold mb-4">Pending Stories ({pendingContent.length})</h2>
        <div className="space-y-3">
          {pendingContent.map((content) => (
            <div
              key={content.id}
              className={`
                p-4 rounded-lg cursor-pointer transition-all duration-200 border-2
                ${selectedContent?.id === content.id
                  ? 'bg-primary-50 border-primary-500 shadow-md'
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300 hover:shadow-sm'
                }
              `}
              onClick={() => {
                console.log('Selected content:', content);
                setSelectedContent(content);
              }}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900 flex-1">
                  {content.title || 'Untitled Story'}
                </h3>
                {content.youtube_url && (
                  <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full ml-2">
                    🎥 Video
                  </span>
                )}
              </div>

              <div className="text-sm text-gray-500 mb-2">
                By {content.submitted_by || 'Unknown'} • {new Date(content.created_at).toLocaleDateString()}
              </div>

              <p className="text-sm text-gray-600 overflow-hidden"
                 style={{
                   display: '-webkit-box',
                   WebkitLineClamp: 2,
                   WebkitBoxOrient: 'vertical' as const,
                   lineHeight: '1.4em',
                   maxHeight: '2.8em'
                 }}>
                {content.rich_content
                  ? content.rich_content.replace(/<[^>]*>/g, '').substring(0, 150) + '...'
                  : content.body.substring(0, 150) + '...'
                }
              </p>
            </div>
          ))}
          
          {pendingContent.length === 0 && (
            <p className="text-gray-500 text-center py-8">
              No pending stories to review! 🎉
            </p>
          )}
        </div>
      </div>

      {/* Right Panel - Story Preview */}
      <div className="bg-white rounded-lg shadow-sm p-4 h-full flex flex-col">
        {selectedContent ? (
          <>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-semibold">
                  {selectedContent.title || 'Untitled Story'}
                </h2>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  selectedContent.approval_status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {selectedContent.approval_status?.toUpperCase()}
                </span>
              </div>

              <div className="text-sm text-gray-500">
                Submitted by <span className="font-medium text-gray-700">{selectedContent.submitted_by || 'Unknown'}</span> on{' '}
                <span className="font-medium">{new Date(selectedContent.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Scrollable Content Area */}
            <div className="flex-1 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-lg border">
              {/* Content Preview */}
              <div className="mb-4">
                <h3 className="text-lg font-medium mb-3 text-gray-900">Story Content</h3>
                <div className="prose prose-sm max-w-none">
                  {selectedContent.rich_content || selectedContent.body ? (
                    <>
                      {selectedContent.rich_content ? (
                        <div
                          className="bg-white p-4 rounded-lg border shadow-sm"
                          dangerouslySetInnerHTML={{
                            __html: selectedContent.rich_content
                          }}
                        />
                      ) : (
                        <div className="bg-white p-4 rounded-lg border shadow-sm">
                          <p className="whitespace-pre-wrap text-gray-800 leading-relaxed text-base">
                            {selectedContent.body}
                          </p>
                        </div>
                      )}

                      {/* Content Length Indicator */}
                      <div className="mt-3 text-xs text-gray-500 bg-gray-100 p-2 rounded">
                        Content length: {selectedContent.rich_content
                          ? selectedContent.rich_content.replace(/<[^>]*>/g, '').length
                          : selectedContent.body.length} characters
                      </div>
                    </>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-yellow-800 text-sm">
                        ⚠️ No content available for this story.
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* YouTube Video Section */}
              {selectedContent.youtube_url ? (
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-3 text-gray-900 flex items-center">
                    📺 Video Content
                    <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                      YouTube
                    </span>
                  </h3>
                  <div className="aspect-video bg-white p-4 rounded-lg border shadow-sm">
                    <iframe
                      width="100%"
                      height="100%"
                      src={`https://www.youtube.com/embed/${extractYouTubeId(selectedContent.youtube_url)}`}
                      title="YouTube video"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="rounded-lg"
                      loading="lazy"
                    ></iframe>
                  </div>
                </div>
              ) : (
                <div className="mt-6">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                    <p className="text-gray-500 text-sm">📹 No video content</p>
                  </div>
                </div>
              )}

              {/* Additional Info */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Content Type:</span>
                    <span className="ml-2 text-gray-600">{selectedContent.content_type}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Target Grade:</span>
                    <span className="ml-2 text-gray-600">
                      {selectedContent.target_grade ? `Grade ${selectedContent.target_grade}` : 'All Grades'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Source:</span>
                    <span className="ml-2 text-gray-600 capitalize">{selectedContent.source}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Status:</span>
                    <span className="ml-2 text-gray-600 capitalize">{selectedContent.approval_status}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons - Fixed at bottom */}
            <div className="flex space-x-4 mt-auto">
              <button
                onClick={() => handleApprove(selectedContent.id)}
                className="flex-1 bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                ✅ Approve & Publish
              </button>
              <button
                onClick={handleRejectClick}
                className="flex-1 bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                ❌ Reject with Reason
              </button>
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500 py-12 flex-1 flex items-center justify-center">
            👈 Select a story from the list to preview
          </div>
        )}
      </div>

      {/* Rejection Dialog */}
      <Dialog
        open={showRejectionDialog}
        onClose={() => setShowRejectionDialog(false)}
        className="fixed inset-0 z-10 overflow-y-auto"
      >
        <div className="flex items-center justify-center min-h-screen">
          <DialogBackdrop className="fixed inset-0 bg-black opacity-30" />

          <div className="relative bg-white rounded-lg max-w-lg w-full mx-4 p-6">
            <DialogTitle className="text-lg font-medium mb-2">
              Reject Story: {selectedContent?.title || 'Untitled'}
            </DialogTitle>

            <p className="text-sm text-gray-500 mb-4">
              Please provide a constructive reason for rejection. This feedback will help the author improve their story.
            </p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rejection Reason *
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
                placeholder="Explain what needs to be improved... (e.g., 'Story needs more detailed content and better formatting')"
                maxLength={500}
              />
              <div className="text-xs text-gray-500 mt-1 text-right">
                {rejectionReason.length}/500 characters
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRejectionDialog(false);
                  setRejectionReason('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                disabled={!rejectionReason.trim()}
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default PendingApprovals;
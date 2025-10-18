import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  BookmarkIcon,
  ShareIcon,
  FlagIcon,
  AcademicCapIcon,
  UserIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { Content } from '../../types';
import { apiService } from '../../services/api';

interface Comment {
  id: string;
  content: string;
  user: string;
  user_name: string;
  text: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

const ContentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  useEffect(() => {
    loadContent();
  }, [id]);

  const loadContent = async () => {
    try {
      setLoading(true);
      const response = await apiService.getContentById(id!);
      setContent(response.data);
      await loadComments();
    } catch (err) {
      setError('Failed to load content');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      const response = await apiService.getComments(id!);
      // Handle both direct array and paginated response
      const commentsData = response.data.results || response.data || [];
      setComments(commentsData);
    } catch (err) {
      console.error('Failed to load comments:', err);
      setComments([]); // Ensure comments is always an array
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      await apiService.createComment(id!, { text: newComment });
      setNewComment('');
      await loadComments(); // Reload comments
    } catch (err) {
      console.error('Failed to submit comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleBookmarkToggle = async () => {
    if (!content) return;

    try {
      await apiService.toggleBookmark(content.id);
      setContent(prev => prev ? { ...prev, is_bookmarked: !prev.is_bookmarked } : null);
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
    }
  };

  const handleShare = async () => {
    if (!content) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: content.title || 'Motivational Content',
          text: content.body,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(content.body);
    }
  };

  const getContentTypeIcon = (contentType: string) => {
    switch (contentType) {
      case 'MOTIVATION':
        return '💪';
      case 'JOKES':
        return '😄';
      case 'QUOTATION':
        return '💭';
      case 'PUZZLE':
        return '🧩';
      default:
        return '📄';
    }
  };

  const getContentTypeColor = (contentType: string) => {
    switch (contentType) {
      case 'MOTIVATION':
        return 'bg-blue-100 text-blue-800';
      case 'JOKES':
        return 'bg-yellow-100 text-yellow-800';
      case 'QUOTATION':
        return 'bg-purple-100 text-purple-800';
      case 'PUZZLE':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const extractYouTubeId = (url: string): string | null => {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const truncateContent = (content: string, maxLines: number = 6): string => {
    if (!content) return '';

    // Split by newlines and count lines
    const lines = content.split('\n');

    if (lines.length <= maxLines) {
      return content;
    }

    // Take first maxLines lines and add ellipsis
    return lines.slice(0, maxLines).join('\n') + '\n...';
  };

  const truncateHtmlContent = (htmlContent: string, maxLines: number = 6): string => {
    if (!htmlContent) return '';

    // Create a temporary div to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;

    // Get text content and split by lines
    const textContent = tempDiv.textContent || tempDiv.innerText || '';
    const lines = textContent.split('\n');

    if (lines.length <= maxLines) {
      return htmlContent;
    }

    // For HTML content, we'll just truncate at a reasonable character limit
    // since line counting in HTML is complex
    const avgCharsPerLine = 80; // Approximate
    const maxChars = maxLines * avgCharsPerLine;

    if (textContent.length <= maxChars) {
      return htmlContent;
    }

    // Find a good breaking point (end of sentence or word)
    let truncatedText = textContent.substring(0, maxChars);
    const lastSentenceEnd = Math.max(
      truncatedText.lastIndexOf('.'),
      truncatedText.lastIndexOf('!'),
      truncatedText.lastIndexOf('?')
    );

    if (lastSentenceEnd > maxChars * 0.7) { // If we can break at a sentence
      truncatedText = truncatedText.substring(0, lastSentenceEnd + 1);
    } else {
      // Break at last space
      const lastSpace = truncatedText.lastIndexOf(' ');
      if (lastSpace > maxChars * 0.8) {
        truncatedText = truncatedText.substring(0, lastSpace);
      }
    }

    return truncatedText + '...';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-700">Loading content...</p>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😵</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The requested content could not be found.'}</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5" />
              <span>Back</span>
            </button>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleBookmarkToggle}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title={content.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
              >
                {content.is_bookmarked ? (
                  <BookmarkSolidIcon className="h-5 w-5 text-primary-600" />
                ) : (
                  <BookmarkIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>

              <button
                onClick={handleShare}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Share"
              >
                <ShareIcon className="h-5 w-5 text-gray-400" />
              </button>

              <button
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Report"
              >
                <FlagIcon className="h-5 w-5 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Content Header */}
          <div className="p-8 pb-6">
            <div className="flex items-center space-x-4 mb-4">
              <span className="text-3xl">{getContentTypeIcon(content.content_type)}</span>
              <div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getContentTypeColor(content.content_type)}`}>
                  {content.content_type}
                </span>
                {content.title && (
                  <h1 className="text-3xl font-bold text-gray-900 mt-2">
                    {content.title}
                  </h1>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="flex items-center space-x-6 text-sm text-gray-500 mb-6">
              <div className="flex items-center space-x-1">
                <CalendarIcon className="h-4 w-4" />
                <span>{new Date(content.published_at).toLocaleDateString()}</span>
              </div>

              {content.target_grade && (
                <div className="flex items-center space-x-1">
                  <AcademicCapIcon className="h-4 w-4" />
                  <span>Grade {content.target_grade}</span>
                </div>
              )}

              <div className="flex items-center space-x-1">
                <UserIcon className="h-4 w-4" />
                <span className="capitalize">{content.source}</span>
              </div>

              {content.submitted_by_name && (
                <div className="flex items-center space-x-1">
                  <span>By {content.submitted_by_name}</span>
                </div>
              )}
            </div>
          </div>

          {/* Content Body */}
          <div className="px-8 pb-8">
            {/* Main Content */}
            <div className="mb-8">
              {content.rich_content ? (
                <div
                  className="prose prose-lg max-w-none text-gray-800 leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: truncateHtmlContent(content.rich_content, 6) }}
                />
              ) : (
                <div className="prose prose-lg max-w-none text-gray-800 leading-relaxed">
                  <p className="whitespace-pre-wrap">{truncateContent(content.body, 6)}</p>
                </div>
              )}
            </div>

            {/* YouTube Video */}
            {content.youtube_url && (
              <div className="mb-8">
                <div className="aspect-video">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${extractYouTubeId(content.youtube_url)}`}
                    title={content.title || 'YouTube video'}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="rounded-lg"
                  ></iframe>
                </div>
              </div>
            )}

            {/* News Article Link */}
            {content.news_url && (
              <div className="mb-8">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">📰</span>
                    <span className="font-medium text-blue-900">Related News Article</span>
                  </div>
                  <a
                    href={content.news_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-700 hover:text-blue-800 font-medium underline break-all"
                  >
                    {content.news_url}
                  </a>
                </div>
              </div>
            )}

            {/* Additional Info */}
            {content.target_school && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Target School:</span> {content.target_school}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Comments Section */}
        <div className="mt-8">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center space-x-2 mb-6">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Comments</h2>
                <span className="text-sm text-gray-500">({comments.length})</span>
              </div>

              {/* Comment Form */}
              <form onSubmit={handleSubmitComment} className="mb-6">
                <div className="flex space-x-3">
                  <div className="flex-1">
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Write a comment..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                      rows={3}
                      maxLength={500}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submittingComment || !newComment.trim()}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submittingComment ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <PaperAirplaneIcon className="h-4 w-4" />
                    )}
                    <span>{submittingComment ? 'Posting...' : 'Post'}</span>
                  </button>
                </div>
              </form>

              {/* Comments List */}
              <div className="space-y-4">
                {comments.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No comments yet. Be the first to comment!</p>
                  </div>
                ) : (
                  comments.map((comment) => (
                    <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="font-medium text-gray-900">{comment.user_name}</span>
                            <span className="text-sm text-gray-500">
                              {new Date(comment.created_at).toLocaleDateString()} at{' '}
                              {new Date(comment.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-gray-700 whitespace-pre-wrap">{comment.text}</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentDetail;

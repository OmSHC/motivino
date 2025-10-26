import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import TiptapEditor from '../Editor/TiptapEditor';

interface UnifiedStoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user: any;
  editContent?: any; // For editing existing content
  defaultContentType?: string; // For pre-selecting content type based on page
}

interface FormData {
  content_type: 'MOTIVATION' | 'JOKES' | 'QUOTATION' | 'PUZZLE' | 'TONGUE_TWISTER';
  title: string;
  body: string;
  rich_content: string;
  youtube_url: string;
  news_url: string;
  target_grade: number | null;
  target_school: string;
}

const UnifiedStoryModal: React.FC<UnifiedStoryModalProps> = ({ 
  isOpen, 
  onClose, 
  onSuccess, 
  user, 
  editContent,
  defaultContentType 
}) => {
  const [formData, setFormData] = useState<FormData>({
    content_type: 'MOTIVATION',
    title: '',
    body: '',
    rich_content: '',
    youtube_url: '',
    news_url: '',
    target_grade: null,
    target_school: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Initialize form data when editing or opening modal
  useEffect(() => {
    if (editContent) {
      setFormData({
        content_type: editContent.content_type || editContent.section || 'MOTIVATION',
        title: editContent.title || '',
        body: editContent.body || '',
        rich_content: editContent.rich_content || '',
        youtube_url: editContent.youtube_url || '',
        news_url: editContent.news_url || '',
        target_grade: editContent.target_grade || null,
        target_school: editContent.target_school || '',
      });
    } else {
      // Reset form for new content with default content type
      const initialContentType = defaultContentType || 'MOTIVATION';
      // Map MIXED to MOTIVATION for submissions
      const validContentType = initialContentType === 'MIXED' ? 'MOTIVATION' : initialContentType;
      setFormData({
        content_type: validContentType as 'MOTIVATION' | 'JOKES' | 'QUOTATION' | 'PUZZLE' | 'TONGUE_TWISTER',
        title: '',
        body: '',
        rich_content: '',
        youtube_url: '',
        news_url: '',
        target_grade: null,
        target_school: '',
      });
    }
    setMessage(null);
  }, [editContent, isOpen, defaultContentType]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'target_grade' ? (value ? parseInt(value) : null) : value
    }));
  };

  const handleRichContentChange = (content: string) => {
    setFormData(prev => ({
      ...prev,
      rich_content: content
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      const submitData = {
        ...formData,
        body: formData.body || (formData.rich_content ? formData.rich_content.replace(/<[^>]*>/g, '').substring(0, 200) : 'Content created via story submission'),
        source: user?.role === 'ADMIN' ? 'admin' : 'user',
      };

      if (editContent) {
        // Update existing content
        await apiService.updateContent(editContent.id, submitData);
        setMessage({ type: 'success', text: 'Content updated successfully!' });
      } else {
        // Create new content - always use user submission endpoint for story submissions
        await apiService.submitStory(submitData);
        setMessage({ type: 'success', text: 'Story submitted successfully!' });
      }
      
      // Reset form and close modal after a short delay
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
      
    } catch (error: any) {
      console.error('Error submitting story:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Failed to submit story. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const extractYouTubeId = (url: string): string | null => {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const youtubeId = extractYouTubeId(formData.youtube_url);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {editContent ? 'Edit Story' : 'Submit Story'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {message && (
            <div className={`p-4 rounded-md ${
              message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {message.text}
            </div>
          )}

          {/* Content Type Selection */}
          <div>
            <label htmlFor="content_type" className="block text-sm font-medium text-gray-700 mb-2">
              Content Type *
            </label>
            <select
              id="content_type"
              name="content_type"
              value={formData.content_type}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="MOTIVATION">💪 Motivation</option>
              <option value="JOKES">😄 Jokes</option>
              <option value="QUOTATION">💭 Quotation</option>
              <option value="PUZZLE">🧩 Puzzle</option>
              <option value="TONGUE_TWISTER">🗣️ Tongue Twister</option>
            </select>
          </div>

          {/* Title - Hidden */}
          <div className="hidden">
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Rich Text Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Main Content *
            </label>
            <TiptapEditor
              content={formData.rich_content}
              onChange={handleRichContentChange}
              placeholder="Start writing your story here... Use the toolbar above for formatting."
              minHeight={400}
            />
            <p className="mt-2 text-sm text-gray-500">
              💡 Tip: Use the toolbar above to format your text. You can add images, links, and see exactly how it will appear!
            </p>
          </div>

          {/* Answer/Plain Text Summary */}
          <div>
            <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
              {formData.content_type === 'PUZZLE' ? 'Answer' : 
               formData.content_type === 'TONGUE_TWISTER' ? 'Tongue Twister Text' : 
               'Plain Text Summary (Optional)'}
            </label>
            <textarea
              id="body"
              name="body"
              value={formData.body}
              onChange={handleInputChange}
              rows={3}
              placeholder={formData.content_type === 'PUZZLE' ? 'Enter the answer to the puzzle...' : 
                        formData.content_type === 'TONGUE_TWISTER' ? 'Enter the tongue twister text...' :
                        'Enter a plain text summary (used as fallback and preview)...'}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* YouTube URL */}
          <div>
            <label htmlFor="youtube_url" className="block text-sm font-medium text-gray-700 mb-2">
              YouTube Video URL (Optional)
            </label>
            <input
              type="url"
              id="youtube_url"
              name="youtube_url"
              value={formData.youtube_url}
              onChange={handleInputChange}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
            {youtubeId && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Video Preview:</p>
                <div className="aspect-video">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${youtubeId}`}
                    title="YouTube video"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="rounded-lg"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Target Grade */}
          <div>
            <label htmlFor="target_grade" className="block text-sm font-medium text-gray-700 mb-2">
              Target Grade (Optional)
            </label>
            <select
              id="target_grade"
              name="target_grade"
              value={formData.target_grade || ''}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Grades</option>
              {Array.from({ length: 12 }, (_, i) => i + 1).map(grade => (
                <option key={grade} value={grade}>Grade {grade}</option>
              ))}
            </select>
          </div>

          {/* Target School */}
          <div>
            <label htmlFor="target_school" className="block text-sm font-medium text-gray-700 mb-2">
              Target School (Optional)
            </label>
            <input
              type="text"
              id="target_school"
              name="target_school"
              value={formData.target_school}
              onChange={handleInputChange}
              placeholder="Enter school name..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isSubmitting ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {editContent ? 'Updating...' : 'Submitting...'}
                </span>
              ) : (
                editContent ? 'Update Story' : 'Submit Story'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UnifiedStoryModal;

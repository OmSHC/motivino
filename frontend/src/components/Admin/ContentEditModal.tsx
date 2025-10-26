import React, { useState, useEffect } from 'react';
import TiptapEditor from '../Editor/TiptapEditor';

interface Content {
  id: string;
  section: string;
  title: string;
  body: string;
  rich_content?: string;
  youtube_url?: string;
  target_grade?: number;
  target_school?: string;
}

interface ContentEditModalProps {
  content: Content;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (id: string, updatedContent: any) => void;
}

const ContentEditModal: React.FC<ContentEditModalProps> = ({ content, isOpen, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    section: content.section,
    title: content.title || '',
    body: content.body || '',
    rich_content: content.rich_content || '',
    youtube_url: content.youtube_url || '',
    target_grade: content.target_grade || null,
    target_school: content.target_school || '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (content) {
      setFormData({
        section: content.section,
        title: content.title || '',
        body: content.body || '',
        rich_content: content.rich_content || '',
        youtube_url: content.youtube_url || '',
        target_grade: content.target_grade || null,
        target_school: content.target_school || '',
      });
    }
  }, [content]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'target_grade' ? (value ? parseInt(value) : null) : value
    }));
  };

  const handleRichContentChange = (value?: string) => {
    setFormData(prev => ({ ...prev, rich_content: value || '' }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onUpdate(content.id, {
        ...formData,
        body: formData.body || formData.rich_content.substring(0, 200) || 'Updated content',
      });
      onClose();
    } catch (error) {
      console.error('Error updating content:', error);
      alert('Failed to update content');
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
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Edit Content</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Category */}
          <div>
            <label htmlFor="section" className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              id="section"
              name="section"
              value={formData.section}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="NEWS">📰 News</option>
              <option value="JOKES">😄 Jokes</option>
              <option value="QUOTATION">💭 Quotation</option>
              <option value="STORY">📖 Story</option>
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

          {/* Rich Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Main Content *
            </label>
            <TiptapEditor
              content={formData.rich_content}
              onChange={handleRichContentChange}
              placeholder="Start writing your content here..."
              minHeight={300}
            />
          </div>

          {/* Plain Text Body */}
          <div>
            <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
              {formData.section === 'STORY' ? 'Answer' : 'Plain Text Summary'}
            </label>
            <textarea
              id="body"
              name="body"
              value={formData.body}
              onChange={handleInputChange}
              rows={2}
              placeholder={formData.section === 'STORY' ? 'Enter the answer to the puzzle...' : 'Enter a plain text summary...'}
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
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
            {youtubeId && (
              <div className="mt-3 aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <iframe
                  width="100%"
                  height="100%"
                  src={`https://www.youtube.com/embed/${youtubeId}`}
                  title="YouTube preview"
                  frameBorder="0"
                  allowFullScreen
                ></iframe>
              </div>
            )}
          </div>

          {/* Target Grade */}
          <div>
            <label htmlFor="target_grade" className="block text-sm font-medium text-gray-700 mb-2">
              Target Grade
            </label>
            <select
              id="target_grade"
              name="target_grade"
              value={formData.target_grade || ''}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Grades</option>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(grade => (
                <option key={grade} value={grade}>Grade {grade}</option>
              ))}
            </select>
          </div>

          {/* Target School */}
          <div>
            <label htmlFor="target_school" className="block text-sm font-medium text-gray-700 mb-2">
              Target School
            </label>
            <input
              type="text"
              id="target_school"
              name="target_school"
              value={formData.target_school}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Buttons */}
          <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.rich_content}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Updating...' : '✅ Update Content'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContentEditModal;

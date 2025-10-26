import React, { useState } from 'react';
import { apiService } from '../../services/api';
import TiptapEditor from '../Editor/TiptapEditor';

interface ContentFormData {
  content_type: 'MOTIVATION' | 'JOKES' | 'QUOTATION' | 'PUZZLE';
  title: string;
  body: string;
  rich_content: string;
  youtube_url: string;
  news_url: string;
  target_grade: number | null;
  target_school: string;
}

const ContentCreationForm: React.FC = () => {
  const [formData, setFormData] = useState<ContentFormData>({
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
      // Prepare data
      const submitData = {
        ...formData,
        body: formData.body || (formData.rich_content ? formData.rich_content.replace(/<[^>]*>/g, '').substring(0, 200) : 'Content created via admin panel'),
        source: 'admin',
      };

      await apiService.createContent(submitData);
      
      setMessage({ type: 'success', text: 'Content created successfully!' });
      
      // Reset form
      setFormData({
        content_type: 'MOTIVATION',
        title: '',
        body: '',
        rich_content: '',
        youtube_url: '',
        news_url: '',
        target_grade: null,
        target_school: '',
      });
    } catch (error: any) {
      console.error('Error creating content:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.error || 'Failed to create content. Please try again.' 
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


  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Content</h2>

      {message && (
        <div className={`mb-4 p-4 rounded-md ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
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
            placeholder="Enter a catchy title..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>


        {/* Rich Text Content with MD Editor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Main Content *
          </label>
          
          <TiptapEditor
            content={formData.rich_content}
            onChange={handleRichContentChange}
            placeholder="Start writing your content here... Use the toolbar above for formatting."
            minHeight={500}
          />
          
          <p className="mt-2 text-sm text-gray-500">
            💡 Tip: Use the toolbar above to format your text. You can add images, links, and see exactly how it will appear!
          </p>
        </div>

        {/* Plain Text Body (Fallback) */}
        <div>
          <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
            {formData.content_type === 'PUZZLE' ? 'Answer' : 'Plain Text Summary (Optional)'}
          </label>
          <textarea
            id="body"
            name="body"
            value={formData.body}
            onChange={handleInputChange}
            rows={3}
            placeholder={formData.content_type === 'PUZZLE' ? 'Enter the answer to the puzzle...' : 'Enter a plain text summary (used as fallback and preview)...'}
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
            <div className="mt-3">
              <p className="text-sm text-gray-600 mb-2">📹 Video Preview:</p>
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <iframe
                  width="100%"
                  height="100%"
                  src={`https://www.youtube.com/embed/${youtubeId}`}
                  title="YouTube video preview"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-write; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          )}
        </div>

        {/* News URL */}
        <div>
          <label htmlFor="news_url" className="block text-sm font-medium text-gray-700 mb-2">
            News Article URL (Optional)
          </label>
          <input
            type="url"
            id="news_url"
            name="news_url"
            value={formData.news_url}
            onChange={handleInputChange}
            placeholder="https://example.com/news-article"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
          {formData.news_url && (
            <div className="mt-2">
              <a
                href={formData.news_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline text-sm"
              >
                🔗 Preview: {formData.news_url}
              </a>
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
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(grade => (
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
            placeholder="Leave empty for all schools"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => {
              setFormData({
                content_type: 'MOTIVATION',
                title: '',
                body: '',
                rich_content: '',
                youtube_url: '',
                news_url: '',
                target_grade: null,
                target_school: '',
              });
              setMessage(null);
            }}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !formData.rich_content}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 font-medium"
          >
            {isSubmitting ? (
              <>
                <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                Creating...
              </>
            ) : (
              '✨ Create Content'
            )}
          </button>
        </div>
      </form>

    </div>
  );
};

export default ContentCreationForm;
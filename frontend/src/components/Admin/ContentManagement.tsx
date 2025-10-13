import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import ContentEditModal from './ContentEditModal';

interface Content {
  id: string;
  section: string;
  title: string;
  body: string;
  rich_content?: string;
  youtube_url?: string;
  target_grade?: number;
  target_school?: string;
  published_at: string;
  is_active: boolean;
}

const ContentManagement: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('ALL');
  const [editingContent, setEditingContent] = useState<Content | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    fetchContents();
  }, [filter]);

  const fetchContents = async () => {
    setLoading(true);
    try {
      const params = filter !== 'ALL' ? { section: filter } : {};
      const response = await apiService.getAdminContent(params);
      setContents(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching contents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this content?')) return;

    try {
      await apiService.deleteContent(id);
      setContents(contents.filter(c => c.id !== id));
    } catch (error) {
      console.error('Error deleting content:', error);
      alert('Failed to delete content');
    }
  };

  const handleEdit = (content: Content) => {
    setEditingContent(content);
    setIsEditModalOpen(true);
  };

  const handleUpdate = async (id: string, updatedData: any) => {
    try {
      await apiService.updateContent(id, updatedData);
      // Refresh the content list
      fetchContents();
    } catch (error) {
      console.error('Error updating content:', error);
      throw error;
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Manage Content</h2>
        
        {/* Filter */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="ALL">All Categories</option>
          <option value="NEWS">News</option>
          <option value="JOKES">Jokes</option>
          <option value="QUOTATION">Quotation</option>
          <option value="STORY">Story</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading content...</p>
        </div>
      ) : contents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No content found. Create some content to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {contents.map((content) => (
            <div key={content.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="inline-block px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {content.section}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(content.published_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {content.title || 'Untitled'}
                  </h3>
                  <p className="text-gray-600 line-clamp-2">
                    {content.body}
                  </p>
                </div>
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => handleEdit(content)}
                    className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleDelete(content.id)}
                    className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingContent && (
        <ContentEditModal
          content={editingContent}
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingContent(null);
          }}
          onUpdate={handleUpdate}
        />
      )}
    </div>
  );
};

export default ContentManagement;

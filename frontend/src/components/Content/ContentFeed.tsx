import React, { useState, useEffect, useCallback } from 'react';
import ContentCard from './ContentCard';
import UnifiedStoryModal from '../Admin/UnifiedStoryModal';
import { Content, User } from '../../types';
import { apiService } from '../../services/api';

interface ContentFeedProps {
  contentType: string;
  user: User | null;
}

// Function to get dynamic submit button label based on content type
const getSubmitButtonLabel = (contentType: string): string => {
  switch (contentType) {
    case 'MIXED':
    case 'MOTIVATION':
      return 'Submit Story';
    case 'JOKES':
      return 'Submit Joke';
    case 'QUOTATION':
      return 'Submit Quote';
    case 'PUZZLE':
      return 'Submit Puzzle';
    case 'TONGUE_TWISTER':
      return 'Submit Tongue Twister';
    case 'SAVED':
      return 'Submit Story';
    default:
      return 'Submit Story';
  }
};

const ContentFeed: React.FC<ContentFeedProps> = ({ contentType, user }) => {
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [isStoryModalOpen, setIsStoryModalOpen] = useState(false);


  const loadContent = useCallback(async (pageNum: number = 1, reset: boolean = false) => {
    try {
      if (pageNum === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      let newContent: Content[] = [];

      if (contentType === 'MIXED') {
        // For homepage mixed content, show latest MOTIVATION content
        const params: any = {
          content_type: 'MOTIVATION',
          limit: 10,
          offset: (pageNum - 1) * 10,
        };

        const response = await apiService.getContent(params);
        newContent = response.data.results || response.data;

        // For mixed content, check if there are more items
        setHasMore(newContent.length === 10);
      } else if (contentType === 'SAVED') {
        // For saved/bookmarked content
        console.log('Loading saved content...');
        const response = await apiService.getBookmarks();
        console.log('Bookmarks API response:', response);
        const bookmarks = response.data.results || response.data || [];
        console.log('Bookmarks array:', bookmarks);

        // Extract content objects from bookmark objects
        newContent = bookmarks.map((bookmark: any) => bookmark.content || bookmark);
        console.log('Extracted content:', newContent);

        // Check if there are more bookmarks
        setHasMore(bookmarks.length === 10);
      } else {
        // Single content type request
        const params: any = {
          content_type: contentType,
          limit: 10,
          offset: (pageNum - 1) * 10,
        };

        // For "For Me" section (MOTIVATION), filter by user's grade
        if (contentType === 'MOTIVATION' && user?.grade) {
          params.grade = user.grade;
        }
        const response = await apiService.getContent(params);
        newContent = response.data.results || response.data;

        // Check if there are more items in this content type
        setHasMore(newContent.length === 10);
      }

      if (reset) {
        setContent(newContent);
      } else {
        setContent(prev => [...prev, ...newContent]);
      }

      setPage(pageNum);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [contentType, user]);

  useEffect(() => {
    loadContent(1, true);
  }, [contentType, user]);



  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      loadContent(page + 1, false);
    }
  };

  const handleBookmarkToggle = () => {
    // Refresh content to update bookmark status
    loadContent(1, true);
  };

  const contentTypeTitles = {
    'MIXED': '🎯 Motivational News',
    'MOTIVATION': '📰 For Me',
    'JOKES': '😄 Jokes',
    'QUOTATION': '💭 Quotations',
    'PUZZLE': '🧩 Puzzles',
    'TONGUE_TWISTER': '🗣️ Tongue Twister',
    'SAVED': '⭐ Saved Items',
  };

  const contentTypeDescriptions = {
    'MIXED': '',
    'MOTIVATION': 'Personalized motivation content for your grade level',
    'JOKES': 'Brighten your day with age-appropriate jokes and humor',
    'QUOTATION': 'Find inspiration in daily quotes from great minds',
    'PUZZLE': 'Challenge your mind with fun brain teasers and puzzles',
    'TONGUE_TWISTER': 'Test your speaking skills with fun tongue twisters',
    'SAVED': 'Your bookmarked content and favorite stories',
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 min-h-full">
      {/* Header */}
      <div className="relative">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {contentTypeTitles[contentType as keyof typeof contentTypeTitles] || contentType}
          </h1>
          <p className="text-gray-600">
            {contentTypeDescriptions[contentType as keyof typeof contentTypeDescriptions] || 'Browse content'}
          </p>
        </div>
        
        {/* Submit Story Button - Top Right */}
        {user && (
          <div className="absolute top-0 right-0">
            <button
              onClick={() => setIsStoryModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-md transition-colors duration-200 flex items-center space-x-2"
            >
              <span>✨</span>
              <span>{getSubmitButtonLabel(contentType)}</span>
            </button>
          </div>
        )}
      </div>



      {/* Content List */}
      {content.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No content found</h3>
          <p className="text-gray-600">
            Try adjusting your filters or check back later for new content.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {content.map((item) => (
            <ContentCard
              key={item.id}
              content={item}
              onBookmarkToggle={handleBookmarkToggle}
            />
          ))}

          {/* Load More Button */}
          {hasMore && (
            <div className="text-center">
              <button
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="btn-primary"
              >
                {loadingMore ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Unified Story Modal */}
      <UnifiedStoryModal
        isOpen={isStoryModalOpen}
        onClose={() => setIsStoryModalOpen(false)}
        onSuccess={() => {
          // Refresh content after successful submission
          loadContent(1, true);
        }}
        user={user}
        defaultContentType={contentType}
      />
    </div>
  );
};

export default ContentFeed;

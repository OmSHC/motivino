import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  BookmarkIcon,
  ShareIcon,
  FlagIcon,
  CalendarIcon,
  UserIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { Content } from '../../types';
import { apiService } from '../../services/api';

interface ContentCardProps {
  content: Content;
  onBookmarkToggle?: () => void;
}

const ContentCard: React.FC<ContentCardProps> = ({ content, onBookmarkToggle }) => {
  const [isBookmarked, setIsBookmarked] = useState(content.is_bookmarked);
  const [isLoading, setIsLoading] = useState(false);

  const handleBookmarkToggle = async () => {
    setIsLoading(true);
    try {
      await apiService.toggleBookmark(content.id);
      setIsBookmarked(!isBookmarked);
      onBookmarkToggle?.();
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShare = async () => {
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
      // You could show a toast notification here
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


  return (
    <div className="card hover:shadow-xl transition-shadow duration-300">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getContentTypeIcon(content.content_type)}</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleBookmarkToggle();
            }}
            disabled={isLoading}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
          >
            {isBookmarked ? (
              <BookmarkSolidIcon className="h-5 w-5 text-primary-600" />
            ) : (
              <BookmarkIcon className="h-5 w-5 text-gray-400" />
            )}
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleShare();
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title="Share"
          >
            <ShareIcon className="h-5 w-5 text-gray-400" />
          </button>
          
          <button
            onClick={(e) => e.stopPropagation()}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title="Report"
          >
            <FlagIcon className="h-5 w-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div 
        className="mb-4 cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors duration-200"
        onClick={() => window.open(`/content/${content.id}`, '_blank')}
        title="Click to open in new tab"
      >
        {content.rich_content ? (
          <div 
            className="prose prose-sm max-w-none text-gray-700 leading-relaxed"
            dangerouslySetInnerHTML={{
              __html: content.rich_content
            }}
          />
        ) : (
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {content.body}
          </p>
        )}
      </div>

      {/* YouTube Video */}
      {content.youtube_url && (
        <div 
          className="mb-4 aspect-video"
          onClick={(e) => e.stopPropagation()}
        >
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
      )}

      {/* Metadata */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <CalendarIcon className="h-4 w-4" />
            <span>
              {new Date(content.published_at).toLocaleDateString()}
            </span>
          </div>
          
          {content.target_grade && (
            <div className="flex items-center space-x-1">
              <AcademicCapIcon className="h-4 w-4" />
              <span>Grade {content.target_grade}</span>
            </div>
          )}
          
          <div className="flex items-center space-x-1">
            <UserIcon className="h-4 w-4" />
            <span>{content.submitted_by_name || content.source}</span>
          </div>
        </div>
        
        {content.target_school && (
          <div className="text-xs bg-gray-100 px-2 py-1 rounded-full">
            {content.target_school}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentCard;

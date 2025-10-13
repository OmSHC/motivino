import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';

interface QuotationBannerProps {
  className?: string;
}

const QuotationBanner: React.FC<QuotationBannerProps> = ({ className = '' }) => {
  const [quote, setQuote] = useState<string>('');
  const [author, setAuthor] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRandomQuote();
  }, []);

  const loadRandomQuote = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDailyQuote();
      const quoteData = response.data;

      if (quoteData && quoteData.body) {
        // Extract quote and author from the body
        const lines = quoteData.body.split('\n').filter((line: string) => line.trim());
        if (lines.length >= 2) {
          setQuote(lines[0].trim());
          setAuthor(lines[1].trim());
        } else {
          setQuote(quoteData.body);
          setAuthor('Unknown');
        }
      }
    } catch (err) {
      console.error('Failed to load quote:', err);
      // Fallback quotes
      const fallbackQuotes = [
        { quote: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
        { quote: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
        { quote: "Innovation distinguishes between a leader and a follower.", author: "Steve Jobs" },
        { quote: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
        { quote: "It is during our darkest moments that we must focus to see the light.", author: "Aristotle" }
      ];

      const randomQuote = fallbackQuotes[Math.floor(Math.random() * fallbackQuotes.length)];
      setQuote(randomQuote.quote);
      setAuthor(randomQuote.author);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 ${className}`}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
          <span className="text-lg font-medium">Loading inspiration...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 ${className}`}>
      <div className="w-full text-center">
        <div className="flex items-center justify-center mb-1">
          <span className="text-xl mr-2">💭</span>
          <span className="text-sm font-medium opacity-90">Daily Inspiration</span>
        </div>
        <blockquote className="text-base font-medium italic mb-1">
          "{quote}"
        </blockquote>
        <cite className="text-xs opacity-90">— {author}</cite>
      </div>
    </div>
  );
};

export default QuotationBanner;

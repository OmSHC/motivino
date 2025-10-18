export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  grade?: number;
  school?: string;
  role: 'USER' | 'ADMIN';
  signup_date: string;
  last_visit_date?: string;
  visit_days_count: number;
  initials: string;
}

export interface Content {
  id: string;
  content_type: 'MOTIVATION' | 'JOKES' | 'QUOTATION' | 'PUZZLE';
  title?: string;
  body: string;
  rich_content?: string;
  youtube_url?: string;
  news_url?: string;
  target_grade?: number | null;
  target_school?: string;
  source: 'openai' | 'admin' | 'user';
  published_at: string;
  created_at: string;
  is_bookmarked: boolean;
  is_active: boolean;
  created_by?: string;
  submitted_by?: string;
  submitted_by_name?: string;
  created_by_name?: string;
  approval_status: 'pending' | 'approved' | 'rejected';
  reviewed_by?: string;
  reviewed_at?: string;
  rejection_reason?: string;
  resubmission_status?: 'none' | 'resubmitted' | 'original';
  original_submission?: string;
}

export interface Bookmark {
  id: string;
  content: Content;
  created_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

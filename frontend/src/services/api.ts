import axios from 'axios';

const API_BASE_URL = '/api';

// Debug logging for API calls
console.log('🚀 API Base URL:', API_BASE_URL);
console.log('🌐 Current location:', window.location.origin);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies in requests
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear both token and cookies on auth failure
      localStorage.removeItem('access_token');
      localStorage.removeItem('session_key');
      // Clear session cookies
      document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // Auth
  signup: (userData: any) => api.post('/users/signup/', userData),
  login: (credentials: any) => api.post('/users/login/', credentials),
  logout: () => api.post('/users/logout/'),
  
  // Google OAuth
  getGoogleAuthUrl: () => api.get('/users/oauth/google/url/'),
  googleOAuthCallback: (code: string) => api.post('/users/oauth/google/callback/', { code }),
  demoLogin: (userData?: any) => api.post('/users/demo/login/', userData),
  
  // Users
  getCurrentUser: () => api.get('/users/me/'),
  updateUser: (data: any) => api.put('/users/me/update/', data),
  trackVisit: () => api.post('/users/track-visit/'),
  
  // Content
  getContent: (params?: any) => {
    // Convert section to content_type if needed for backward compatibility
    if (params?.section && !params?.content_type) {
      params.content_type = params.section;
      delete params.section;
    }
    return api.get('/content/', { params });
  },
  getContentById: (id: string) => api.get(`/content/${id}/`),
  getDailyQuote: () => api.get('/content/quote/'),
  toggleBookmark: (id: string) => api.post(`/content/${id}/bookmark/`),
  getBookmarks: () => api.get('/content/bookmarks/'),
  
  // Admin Content Management
  createContent: (data: any) => api.post('/content/admin/create/', data),
  updateContent: (id: string, data: any) => api.put(`/content/admin/${id}/update/`, data),
  deleteContent: (id: string) => api.delete(`/content/admin/${id}/delete/`),
  getAdminContent: (params?: any) => api.get('/content/admin/', { params }),
  
  // User Story Submission
  submitStory: (data: any) => api.post('/content/submit-story/', data),
  getMySubmissions: () => api.get('/content/my-submissions/'),
  deleteSubmission: (id: string) => api.delete(`/content/submissions/${id}/delete/`),
  
  // Admin Approval
  getPendingSubmissions: () => api.get('/content/admin/pending/'),
  approveSubmission: (id: string) => api.post(`/content/admin/${id}/approve/`),
  rejectSubmission: (id: string, rejectionReason: string) =>
    api.post(`/content/admin/${id}/reject/`, { rejection_reason: rejectionReason }),
  resubmit: (id: string, data: any) => api.post(`/content/resubmit/${id}/`, data),

  // Comments
  getComments: (contentId: string) => api.get(`/content/${contentId}/comments/`),
  createComment: (contentId: string, data: any) => api.post(`/content/${contentId}/comments/`, data),
  
  // Core
  generateContent: () => api.post('/core/generate-content/'),
  generateGradeContent: (grade: number, count: number = 3) => 
    api.post('/core/generate-grade-content/', { grade, count }),
  generateQuote: () => api.post('/core/generate-quote/'),
};

export default api;

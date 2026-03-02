import apiClient from './client';

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  telegram_username?: string;
}

export interface UserProfile {
  dob?: string;
  gender?: string;
  education_level?: string;
  education_stream?: string;
  category?: string;
  state?: string;
  exam_interests?: string[];
}

export interface Notification {
  id: number;
  title: string;
  organization?: string;
  exam_type?: string;
  last_date?: string;
  min_age?: number;
  max_age?: number;
  education_required?: string;
  total_vacancies?: number;
  vacancy_by_category?: Record<string, number>;
  age_relaxation?: Record<string, number>;
  original_pdf_url?: string;
  official_website_url?: string;
  eligibility_status?: string;
  eligibility_reasons?: string[];
  created_at?: string;
}

// Auth
export const authAPI = {
  login: (data: LoginData) => apiClient.post('/api/auth/login', data),
  register: (data: RegisterData) => apiClient.post('/api/auth/register', data),
};

// User
export const userAPI = {
  getMe: () => apiClient.get('/api/users/me'),
  getProfile: () => apiClient.get('/api/users/profile'),
  updateProfile: (data: UserProfile) => apiClient.put('/api/users/profile', data),
  updateTelegramChatId: (chatId: number) =>
    apiClient.put('/api/users/telegram-chat-id', { telegram_chat_id: chatId }),
};

// Notifications
export const notificationAPI = {
  list: (params?: { page?: number; per_page?: number; exam_type?: string; search?: string }) =>
    apiClient.get('/api/notifications', { params }),
  getById: (id: number) => apiClient.get(`/api/notifications/${id}`),
  select: (notificationIds: number[]) =>
    apiClient.post('/api/notifications/select', { notification_ids: notificationIds }),
};

// Admin
export const adminAPI = {
  listChannels: () => apiClient.get('/api/admin/channels'),
  addChannel: (data: { channel_username: string; channel_name?: string }) =>
    apiClient.post('/api/admin/channels', data),
  removeChannel: (id: number) => apiClient.delete(`/api/admin/channels/${id}`),
  toggleChannel: (id: number) => apiClient.patch(`/api/admin/channels/${id}/toggle`),
  getStats: () => apiClient.get('/api/admin/stats'),
};

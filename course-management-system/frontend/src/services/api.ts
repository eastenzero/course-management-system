import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理通用错误
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login/', credentials),
  
  logout: () =>
    api.post('/auth/logout/'),
  
  getCurrentUser: () =>
    api.get('/auth/user/'),
  
  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh/', { refresh: refreshToken }),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.put('/auth/change-password/', data),

  verifyCurrentPassword: (password: string) =>
    api.post('/auth/verify-password/', { password }),
};

// 课程API
export const courseAPI = {
  getCourses: (params?: any) =>
    api.get('/courses/', { params }),
  
  getCourse: (id: number) =>
    api.get(`/courses/${id}/`),
  
  createCourse: (data: any) =>
    api.post('/courses/', data),
  
  updateCourse: (id: number, data: any) =>
    api.put(`/courses/${id}/`, data),
  
  deleteCourse: (id: number) =>
    api.delete(`/courses/${id}/`),
  
  getCourseStats: () =>
    api.get('/courses/stats/'),
};

// 用户API
export const userAPI = {
  getUsers: (params?: any) =>
    api.get('/users/', { params }),
  
  getUser: (id: number) =>
    api.get(`/users/${id}/`),
  
  createUser: (data: any) =>
    api.post('/users/', data),
  
  updateUser: (id: number, data: any) =>
    api.put(`/users/${id}/`, data),
  
  deleteUser: (id: number) =>
    api.delete(`/users/${id}/`),
  
  getUserStats: () =>
    api.get('/users/stats/'),

  getPreferences: () =>
    api.get('/users/preferences/'),

  updatePreferences: (data: any) =>
    api.patch('/users/preferences/', data),
};

// 教室API
export const classroomAPI = {
  getClassrooms: (params?: any) =>
    api.get('/classrooms/', { params }),
  
  getClassroom: (id: number) =>
    api.get(`/classrooms/${id}/`),
  
  createClassroom: (data: any) =>
    api.post('/classrooms/', data),
  
  updateClassroom: (id: number, data: any) =>
    api.put(`/classrooms/${id}/`, data),
  
  deleteClassroom: (id: number) =>
    api.delete(`/classrooms/${id}/`),
};

// 排课API
export const scheduleAPI = {
  getSchedules: (params?: any) =>
    api.get('/schedules/', { params }),
  
  getSchedule: (id: number) =>
    api.get(`/schedules/${id}/`),
  
  createSchedule: (data: any) =>
    api.post('/schedules/', data),
  
  updateSchedule: (id: number, data: any) =>
    api.put(`/schedules/${id}/`, data),
  
  deleteSchedule: (id: number) =>
    api.delete(`/schedules/${id}/`),
  
  checkConflicts: (data: any) =>
    api.post('/schedules/check-conflicts/', data),

  exportSchedules: (params?: any) =>
    api.get('/schedules/export/', {
      params,
      responseType: 'blob'  // 重要：设置响应类型为blob以处理二进制文件
    }),
};

// 分析API
export const analyticsAPI = {
  getDashboardStats: () =>
    api.get('/analytics/dashboard/'),
  
  getCourseAnalytics: (params?: any) =>
    api.get('/analytics/courses/', { params }),
  
  getUserAnalytics: (params?: any) =>
    api.get('/analytics/users/', { params }),
  
  getEnrollmentTrends: (params?: any) =>
    api.get('/analytics/enrollment-trends/', { params }),
};

// 教师API
export const teacherApi = {
  getProfile: () =>
    api.get('/teachers/profile/'),

  updateProfile: (data: any) =>
    api.put('/teachers/profile/', data),

  uploadAvatar: (formData: FormData) =>
    api.post('/teachers/profile/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
};

// 成绩API
export const gradeApi = {
  getCourseGrades: (courseId: number) =>
    api.get(`/grades/course/${courseId}/`),

  getGradeRecords: (params?: any) =>
    api.get('/grades/', { params }),

  updateGrade: (data: any) =>
    api.post('/grades/', data),

  batchUpdateGrades: (grades: any[]) =>
    api.post('/grades/batch/', { grades }),

  deleteGrade: (id: number) =>
    api.delete(`/grades/${id}/`),

  batchDeleteGrades: (ids: number[]) =>
    api.post('/grades/batch-delete/', { ids }),

  publishGrades: (courseId: number) =>
    api.post(`/grades/course/${courseId}/publish/`),

  exportGrades: (params?: any) =>
    api.get('/grades/export/', { params, responseType: 'blob' }),
};

// 课程API扩展
export const courseApi = {
  ...courseAPI,

  getTeacherCourses: () =>
    api.get('/courses/teacher/'),
};

// 排课API扩展
export const scheduleApi = {
  ...scheduleAPI,

  getTeacherSchedules: (params?: any) =>
    api.get('/schedules/teacher/', { params }),
};

// 导出API客户端实例
export const apiClient = api;

// 通知API
export const notificationAPI = {
  getNotifications: (params?: any) =>
    api.get('/notifications/', { params }),

  getNotification: (id: number) =>
    api.get(`/notifications/${id}/`),

  markAsRead: (notificationIds: number[]) =>
    api.post('/notifications/mark-read/', { notification_ids: notificationIds }),

  markAllAsRead: () =>
    api.post('/notifications/mark-all-read/'),

  getUnreadCount: () =>
    api.get('/notifications/unread-count/'),

  getPreferences: () =>
    api.get('/notifications/preferences/'),

  updatePreferences: (data: any) =>
    api.put('/notifications/preferences/', data),

  createNotification: (data: any) =>
    api.post('/notifications/create/', data),
};

// 文件管理API
export const fileAPI = {
  getFiles: (params?: any) =>
    api.get('/files/', { params }),

  getFile: (id: string) =>
    api.get(`/files/${id}/`),

  uploadFile: (formData: FormData) =>
    api.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  deleteFile: (id: string) =>
    api.delete(`/files/${id}/`),

  bulkOperation: (data: { file_ids: string[]; action: string }) =>
    api.post('/files/bulk-operation/', data),

  getStats: () =>
    api.get('/files/stats/'),

  createShare: (data: any) =>
    api.post('/files/shares/', data),

  getShares: (params?: any) =>
    api.get('/files/shares/', { params }),

  deleteShare: (id: string) =>
    api.delete(`/files/shares/${id}/`),
};

// 导出学生API
export { studentAPI } from './studentAPI';

// 导出教师API
export { teacherAPI } from './teacherAPI';

export default api;

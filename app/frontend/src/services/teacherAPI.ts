import { apiClient } from './api';

export interface TeacherProfile {
  id: number;
  user_info: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    employee_id: string;
    department: string;
  };
  title: string;
  title_display: string;
  full_name: string;
  research_area: string;
  office_location: string;
  office_hours: string;
  teaching_experience: number;
  education_background: string;
  office_phone: string;
  personal_website: string;
  teaching_courses_count: number;
  is_active_teacher: boolean;
}

export interface TeacherDashboardData {
  teacher_info: TeacherProfile;
  total_courses: number;
  current_semester_courses: number;
  total_students: number;
  course_statistics: {
    by_type: Record<string, number>;
    by_department: Record<string, number>;
  };
  today_schedule: any[];
  pending_tasks: Array<{
    type: string;
    title: string;
    description: string;
    count: number;
    course_id?: number;
  }>;
  recent_notices: any[];
}

export interface TeacherCourse {
  id: number;
  code: string;
  name: string;
  credits: number;
  hours: number;
  course_type: string;
  department: string;
  semester: string;
  academic_year: string;
  description: string;
  objectives: string;
  teachers_info: any[];
  max_students: number;
  min_students: number;
  current_enrollment: number;
  enrollment_statistics: {
    total: number;
    by_status: Record<string, number>;
  };
  grade_statistics: {
    total_graded: number;
    average_score: number;
    grade_distribution: Record<string, number>;
    pass_rate: number;
  };
  is_active: boolean;
  is_published: boolean;
}

export interface CourseStudent {
  id: number;
  student_info: {
    id: number;
    username: string;
    name: string;
    student_id: string;
    email: string;
    department: string;
    major: string;
    class_name: string;
  };
  enrollment_info: {
    enrolled_at: string;
    status: string;
    status_display: string;
    is_active: boolean;
  };
  progress_info: {
    attendance_rate: number;
    assignment_completion: number;
    participation_score: number;
  };
  score: number | null;
  grade: string;
}

export interface GradeEntry {
  id: number;
  student: number;
  student_name: string;
  student_id: string;
  course: number;
  course_name: string;
  score: number | null;
  grade: string;
  status: string;
}

export interface TeachingSchedule {
  course_id: number;
  course_name: string;
  course_code: string;
  student_count: number;
  classroom: string;
  time_slot: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  week_range: string;
}

export interface TeacherNotice {
  id: number;
  course_info: {
    id: number;
    code: string;
    name: string;
    semester: string;
  };
  title: string;
  content: string;
  notice_type: string;
  notice_type_display: string;
  priority: string;
  priority_display: string;
  is_published: boolean;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CourseGradeStatistics {
  course_info: {
    id: number;
    name: string;
    code: string;
  };
  student_statistics: {
    total_students: number;
    graded_students: number;
    ungraded_students: number;
  };
  grade_statistics: {
    average_score: number;
    max_score: number;
    min_score: number;
    pass_rate: number;
    grade_distribution: Record<string, number>;
  };
}

export const teacherAPI = {
  // 获取教师档案
  getProfile: () => 
    apiClient.get<TeacherProfile>('/teachers/profile/'),

  // 更新教师档案
  updateProfile: (data: Partial<TeacherProfile>) =>
    apiClient.put<TeacherProfile>('/teachers/profile/', data),

  // 上传头像
  uploadAvatar: (formData: FormData) =>
    apiClient.post('/teachers/profile/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // 获取仪表板数据
  getDashboard: () =>
    apiClient.get<TeacherDashboardData>('/teachers/dashboard/'),

  // 获取我的课程
  getMyCourses: () =>
    apiClient.get<TeacherCourse[]>('/teachers/my-courses/'),

  // 获取课程学生列表
  getCourseStudents: (courseId: number, params?: {
    status?: string;
    search?: string;
  }) =>
    apiClient.get<CourseStudent[]>(`/teachers/course/${courseId}/students/`, { params }),

  // 批量录入成绩
  batchGradeEntry: (grades: Array<{
    enrollment_id: number;
    score: number;
  }>) =>
    apiClient.post('/teachers/grades/batch/', { grades }),

  // 更新单个成绩
  updateGrade: (enrollmentId: number, data: {
    score: number;
    grade?: string;
  }) =>
    apiClient.put(`/teachers/grade/${enrollmentId}/`, data),

  // 获取课程成绩统计
  getCourseGradeStatistics: (courseId: number) =>
    apiClient.get<CourseGradeStatistics>(`/teachers/course/${courseId}/grade-stats/`),

  // 获取教学安排
  getSchedule: (params?: {
    semester?: string;
    week?: string;
  }) =>
    apiClient.get<TeachingSchedule[]>('/teachers/schedule/', { params }),

  // 获取通知列表
  getNotices: (params?: {
    course_id?: number;
  }) =>
    apiClient.get<TeacherNotice[]>('/teachers/notices/', { params }),

  // 创建通知
  createNotice: (data: {
    course: number;
    title: string;
    content: string;
    notice_type: string;
    priority: string;
  }) =>
    apiClient.post<TeacherNotice>('/teachers/notices/', data),

  // 更新通知
  updateNotice: (noticeId: number, data: Partial<TeacherNotice>) =>
    apiClient.put<TeacherNotice>(`/teachers/notice/${noticeId}/`, data),

  // 删除通知
  deleteNotice: (noticeId: number) =>
    apiClient.delete(`/teachers/notice/${noticeId}/`),

  // 发布通知
  publishNotice: (noticeId: number) =>
    apiClient.post(`/teachers/notice/${noticeId}/publish/`),

  // 成绩分析相关API

  // 获取课程成绩分布
  getCourseGradeDistribution: (courseId: number) =>
    apiClient.get(`/courses/${courseId}/grade-distribution/`),

  // 获取学生成绩趋势
  getStudentGradeTrend: (studentId: number, semester?: string) =>
    apiClient.get(`/courses/students/${studentId}/grade-trend/`, {
      params: semester ? { semester } : {}
    }),

  // 获取课程难度分析
  getCourseDifficultyAnalysis: (courseId: number) =>
    apiClient.get(`/courses/${courseId}/difficulty-analysis/`),

  // 获取班级成绩对比
  getClassGradeComparison: (className: string, semester: string) =>
    apiClient.get('/courses/class-comparison/', {
      params: { class_name: className, semester }
    }),

  // 导出成绩数据
  exportGrades: (courseId: number, format: 'excel' | 'csv' = 'excel', options?: {
    include_details?: boolean;
    include_statistics?: boolean;
  }) =>
    apiClient.get(`/courses/${courseId}/grades/export/`, {
      params: { format, ...options },
      responseType: 'blob'
    }),

  // 下载成绩模板
  downloadGradeTemplate: (courseId: number) =>
    apiClient.get(`/courses/${courseId}/grades/template/`, {
      responseType: 'blob'
    }),

  // 导入成绩
  importGrades: (courseId: number, grades: Array<{
    student_id: string;
    score: number;
  }>) =>
    apiClient.post(`/courses/${courseId}/grades/import/`, { grades }),
};

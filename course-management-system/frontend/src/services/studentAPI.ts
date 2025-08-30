import { apiClient } from './api';

export interface StudentProfile {
  id: number;
  user_info: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    student_id: string;
    department: string;
  };
  admission_year: number;
  major: string;
  class_name: string;
  gpa: number;
  total_credits: number;
  completed_credits: number;
  remaining_credits: number;
  completion_rate: number;
  enrollment_status: string;
  enrollment_status_display: string;
  emergency_contact: string;
  emergency_phone: string;
}

export interface DashboardData {
  student_info: StudentProfile;
  total_courses: number;
  current_semester_courses: number;
  completed_courses: number;
  average_score: number;
  latest_grades: any[];
  today_schedule: any[];
  notifications: any[];
  upcoming_deadlines: any[];
}

export interface AvailableCourse {
  id: number;
  code: string;
  name: string;
  credits: number;
  hours: number;
  course_type: string;
  department: string;
  semester: string;
  description: string;
  teachers_info: Array<{
    id: number;
    name: string;
    employee_id: string;
  }>;
  max_students: number;
  current_enrollment: number;
  enrollment_info: {
    current: number;
    max: number;
    available: number;
    is_full: boolean;
  };
  can_enroll: boolean;
  conflict_info: any[];
  is_published: boolean;
}

export interface Enrollment {
  id: number;
  course_info: {
    id: number;
    code: string;
    name: string;
    credits: number;
    hours: number;
    course_type: string;
    department: string;
    semester: string;
    description: string;
    teachers_info: any[];
  };
  status: string;
  status_display: string;
  score: number | null;
  grade: string;
  grade_display: string;
  enrolled_at: string;
  is_active: boolean;
}

export interface CourseSchedule {
  course_id: number;
  course_name: string;
  course_code: string;
  teacher_name: string;
  classroom: string;
  time_slot: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  week_range: string;
}

export interface GradeRecord {
  id: number;
  course_info: {
    id: number;
    code: string;
    name: string;
  };
  score: number;
  grade: string;
  status: string;
  enrolled_at: string;
}

export interface GPAStatistics {
  overall_gpa: number;
  semester_gpa: Record<string, number>;
  credit_summary: {
    total_credits: number;
    completed_credits: number;
    gpa_credits: number;
  };
  grade_distribution: Record<string, number>;
}

export const studentAPI = {
  // 获取学生档案
  getProfile: () => 
    apiClient.get<StudentProfile>('/students/profile/'),

  // 更新学生档案
  updateProfile: (data: Partial<StudentProfile>) =>
    apiClient.put<StudentProfile>('/students/profile/', data),

  // 获取仪表板数据
  getDashboard: () =>
    apiClient.get<DashboardData>('/students/dashboard/'),

  // 获取可选课程
  getAvailableCourses: (params?: {
    semester?: string;
    department?: string;
    course_type?: string;
    search?: string;
  }) =>
    apiClient.get<AvailableCourse[]>('/students/available-courses/', { params }),

  // 选课
  enrollCourse: (courseId: number) =>
    apiClient.post('/students/enroll/', { course_id: courseId }),

  // 退课
  dropCourse: (courseId: number) =>
    apiClient.delete(`/students/drop/${courseId}/`),

  // 检查选课冲突
  checkConflicts: (courseIds: number[]) =>
    apiClient.post('/students/check-conflicts/', { course_ids: courseIds }),

  // 获取我的课程
  getMyCourses: () =>
    apiClient.get<Enrollment[]>('/students/my-courses/'),

  // 获取课程表
  getSchedule: (params?: {
    semester?: string;
    week?: string;
  }) =>
    apiClient.get<CourseSchedule[]>('/students/schedule/', { params }),

  // 获取成绩列表
  getGrades: (params?: {
    semester?: string;
    academic_year?: string;
  }) =>
    apiClient.get<GradeRecord[]>('/students/grades/', { params }),

  // 获取GPA统计
  getGPAStatistics: () =>
    apiClient.get<GPAStatistics>('/students/gpa/'),

  // 导出成绩单
  exportGrades: (params?: {
    semester?: string;
    academic_year?: string;
  }) =>
    apiClient.get('/students/grades/export/', { 
      params,
      responseType: 'blob'
    }),

  // 导出课程表
  exportSchedule: (params?: {
    semester?: string;
  }) =>
    apiClient.get('/students/schedule/export/', { 
      params,
      responseType: 'blob'
    }),
};

import { api } from './index';
import type { Course, CourseStatus, PaginatedResponse } from '../types/index';

// 课程相关API
export const courseAPI = {
  // 获取课程列表
  getCourses: (
    params: {
      page?: number;
      pageSize?: number;
      search?: string;
      status?: CourseStatus;
      department?: string;
      semester?: string;
      teacher?: string;
    } = {}
  ): Promise<{ data: PaginatedResponse<Course> }> => {
    const queryParams = {
      page: params.page || 1,
      page_size: params.pageSize || 10,
      search: params.search,
      status: params.status,
      department: params.department,
      semester: params.semester,
      teacher: params.teacher,
    };

    // 过滤掉undefined的参数
    const filteredParams = Object.fromEntries(
      Object.entries(queryParams).filter(([_, value]) => value !== undefined)
    );

    return api.get('/courses/', { params: filteredParams });
  },

  // 获取课程详情
  getCourseById: (id: string | number): Promise<{ data: Course }> => {
    return api.get(`/courses/${id}/`);
  },

  // 创建课程
  createCourse: (courseData: Partial<Course>): Promise<{ data: Course }> => {
    return api.post('/courses/', courseData);
  },

  // 更新课程
  updateCourse: (
    id: string | number,
    courseData: Partial<Course>
  ): Promise<{ data: Course }> => {
    return api.patch(`/courses/${id}/`, courseData);
  },

  // 删除课程
  deleteCourse: (id: string | number): Promise<{ data: any }> => {
    return api.delete(`/courses/${id}/`);
  },

  // 批量删除课程
  batchDeleteCourses: (ids: (string | number)[]): Promise<{ data: any }> => {
    return api.post('/courses/batch-delete/', { ids });
  },

  // 复制课程
  copyCourse: (
    id: string | number,
    data: {
      name: string;
      code: string;
      semester: string;
    }
  ): Promise<{ data: Course }> => {
    return api.post(`/courses/${id}/copy/`, data);
  },

  // 获取课程统计信息
  getCourseStats: (id: string | number): Promise<{ data: any }> => {
    return api.get(`/courses/${id}/stats/`);
  },

  // 获取课程学生列表
  getCourseStudents: (id: string | number): Promise<{ data: any[] }> => {
    return api.get(`/courses/${id}/students/`);
  },

  // 添加学生到课程
  addStudentToCourse: (
    courseId: string | number,
    studentId: string | number
  ): Promise<{ data: any }> => {
    return api.post(`/courses/${courseId}/students/`, {
      student_id: studentId,
    });
  },

  // 从课程中移除学生
  removeStudentFromCourse: (
    courseId: string | number,
    studentId: string | number
  ): Promise<{ data: any }> => {
    return api.delete(`/courses/${courseId}/students/${studentId}/`);
  },

  // 批量添加学生
  batchAddStudents: (
    courseId: string | number,
    studentIds: (string | number)[]
  ): Promise<{ data: any }> => {
    return api.post(`/courses/${courseId}/students/batch-add/`, {
      student_ids: studentIds,
    });
  },

  // 导入学生（通过文件）
  importStudents: (
    courseId: string | number,
    file: File
  ): Promise<{ data: any }> => {
    return api.upload(`/courses/${courseId}/students/import/`, file);
  },

  // 导出课程数据
  exportCourse: (
    id: string | number,
    format: 'xlsx' | 'csv' | 'pdf' = 'xlsx'
  ): Promise<void> => {
    return api.download(
      `/courses/${id}/export/?format=${format}`,
      `course_${id}.${format}`
    );
  },

  // 获取课程先修关系
  getPrerequisites: (id: string | number): Promise<{ data: Course[] }> => {
    return api.get(`/courses/${id}/prerequisites/`);
  },

  // 设置课程先修关系
  setPrerequisites: (
    id: string | number,
    prerequisiteIds: (string | number)[]
  ): Promise<{ data: any }> => {
    return api.post(`/courses/${id}/prerequisites/`, {
      prerequisite_ids: prerequisiteIds,
    });
  },

  // 获取可用的学期列表
  getSemesters: (): Promise<{ data: string[] }> => {
    return api.get('/courses/semesters/');
  },

  // 获取可用的院系列表
  getDepartments: (): Promise<{ data: string[] }> => {
    return api.get('/courses/departments/');
  },

  // 搜索课程（自动完成）
  searchCourses: (query: string): Promise<{ data: Course[] }> => {
    return api.get('/courses/search/', { params: { q: query } });
  },
};

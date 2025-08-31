import { api } from './index';
import type { Schedule, TimeSlot, Conflict } from '../types/index';

// 课程表相关API
export const scheduleAPI = {
  // 获取时间段列表
  getTimeSlots: (): Promise<{ data: TimeSlot[] }> => {
    return api.get('/schedules/timeslots/simple/');
  },

  // 获取课程表列表
  getSchedules: (
    params: {
      week?: number;
      semester?: string;
      teacher?: string;
      classroom?: string;
      course?: string;
      status?: string;
      start_date?: string;
      end_date?: string;
    } = {}
  ): Promise<{ data: Schedule[] }> => {
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([_, value]) => value !== undefined)
    );

    return api.get('/schedules/', { params: filteredParams });
  },

  // 获取课程表详情
  getScheduleById: (id: string | number): Promise<{ data: Schedule }> => {
    return api.get(`/schedules/${id}/`);
  },

  // 创建课程安排
  createSchedule: (
    scheduleData: Partial<Schedule>
  ): Promise<{ data: Schedule }> => {
    return api.post('/schedules/', scheduleData);
  },

  // 更新课程安排
  updateSchedule: (
    id: string | number,
    scheduleData: Partial<Schedule>
  ): Promise<{ data: Schedule }> => {
    return api.patch(`/schedules/${id}/`, scheduleData);
  },

  // 删除课程安排
  deleteSchedule: (id: string | number): Promise<{ data: any }> => {
    return api.delete(`/schedules/${id}/`);
  },

  // 批量创建课程安排
  batchCreateSchedules: (
    schedules: Partial<Schedule>[]
  ): Promise<{ data: Schedule[] }> => {
    return api.post('/schedules/batch-create/', { schedules });
  },

  // 批量删除课程安排
  batchDeleteSchedules: (ids: (string | number)[]): Promise<{ data: any }> => {
    return api.post('/schedules/batch-delete/', { ids });
  },

  // 获取时间段列表
  getTimeSlots: (): Promise<{ data: TimeSlot[] }> => {
    return api.get('/time-slots/');
  },

  // 创建时间段
  createTimeSlot: (
    timeSlotData: Partial<TimeSlot>
  ): Promise<{ data: TimeSlot }> => {
    return api.post('/time-slots/', timeSlotData);
  },

  // 更新时间段
  updateTimeSlot: (
    id: string | number,
    timeSlotData: Partial<TimeSlot>
  ): Promise<{ data: TimeSlot }> => {
    return api.patch(`/time-slots/${id}/`, timeSlotData);
  },

  // 删除时间段
  deleteTimeSlot: (id: string | number): Promise<{ data: any }> => {
    return api.delete(`/time-slots/${id}/`);
  },

  // 检测冲突
  detectConflicts: (
    params: {
      week?: number;
      semester?: string;
      teacher?: string;
      classroom?: string;
    } = {}
  ): Promise<{ data: Conflict[] }> => {
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([_, value]) => value !== undefined)
    );

    return api.get('/schedules/conflicts/', { params: filteredParams });
  },

  // 解决冲突
  resolveConflict: (
    conflictId: string,
    solution: any
  ): Promise<{ data: any }> => {
    return api.post(`/schedules/conflicts/${conflictId}/resolve/`, solution);
  },

  // 自动排课
  autoSchedule: (params: {
    semester: string;
    courses: string[];
    constraints?: {
      teacher_preferences?: any;
      classroom_preferences?: any;
      time_preferences?: any;
      avoid_conflicts?: boolean;
    };
    algorithm?: 'genetic' | 'greedy' | 'constraint';
  }): Promise<{ data: Schedule[] }> => {
    return api.post('/schedules/auto-schedule/', params);
  },

  // 获取自动排课状态
  getAutoScheduleStatus: (taskId: string): Promise<{ data: any }> => {
    return api.get(`/schedules/auto-schedule/status/${taskId}/`);
  },

  // 取消自动排课
  cancelAutoSchedule: (taskId: string): Promise<{ data: any }> => {
    return api.post(`/schedules/auto-schedule/cancel/${taskId}/`);
  },

  // 验证课程表
  validateSchedule: (
    scheduleData: Partial<Schedule>
  ): Promise<{ data: any }> => {
    return api.post('/schedules/validate/', scheduleData);
  },

  // 获取可用时间段
  getAvailableTimeSlots: (params: {
    teacher?: string;
    classroom?: string;
    date?: string;
    week?: number;
  }): Promise<{ data: TimeSlot[] }> => {
    return api.get('/schedules/available-slots/', { params });
  },

  // 获取教师课程表
  getTeacherSchedule: (
    teacherId: string | number,
    params: {
      week?: number;
      semester?: string;
    } = {}
  ): Promise<{ data: Schedule[] }> => {
    return api.get(`/schedules/teacher/${teacherId}/`, { params });
  },

  // 获取学生课程表
  getStudentSchedule: (
    studentId: string | number,
    params: {
      week?: number;
      semester?: string;
    } = {}
  ): Promise<{ data: Schedule[] }> => {
    return api.get(`/schedules/student/${studentId}/`, { params });
  },

  // 获取教室课程表
  getClassroomSchedule: (
    classroomId: string | number,
    params: {
      week?: number;
      semester?: string;
    } = {}
  ): Promise<{ data: Schedule[] }> => {
    return api.get(`/schedules/classroom/${classroomId}/`, { params });
  },

  // 导出课程表
  exportSchedule: (params: {
    format: 'xlsx' | 'csv' | 'pdf' | 'ics';
    week?: number;
    semester?: string;
    teacher?: string;
    student?: string;
    classroom?: string;
  }): Promise<void> => {
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([_, value]) => value !== undefined)
    );
    const queryString = new URLSearchParams(
      filteredParams as Record<string, string>
    ).toString();

    return api.download(
      `/schedules/export/?${queryString}`,
      `schedule.${params.format}`
    );
  },

  // 导入课程表
  importSchedule: (
    file: File,
    params: {
      semester: string;
      overwrite?: boolean;
    }
  ): Promise<{ data: any }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('semester', params.semester);
    if (params.overwrite) {
      formData.append('overwrite', 'true');
    }

    return api.post('/schedules/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 复制课程表到新学期
  copyScheduleToSemester: (params: {
    from_semester: string;
    to_semester: string;
    courses?: string[];
    teachers?: string[];
  }): Promise<{ data: any }> => {
    return api.post('/schedules/copy-semester/', params);
  },
};

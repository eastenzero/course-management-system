import axios from 'axios';

// 模拟排课API - 直接读取本地JSON文件
export const mockScheduleAPI = {
  getSchedules: async (params?: any) => {
    try {
      // 直接读取本地JSON文件 - 使用绝对路径确保正确访问
      const response = await fetch('http://localhost:8080/data/schedules.json');
      const data = await response.json();
      
      // 模拟分页和过滤
      let schedules = data.schedules || [];
      
      // 根据参数过滤
      if (params?.semester) {
        schedules = schedules.filter((schedule: any) => schedule.semester === params.semester);
      }
      
      if (params?.teacher) {
        schedules = schedules.filter((schedule: any) => schedule.teacher.includes(params.teacher));
      }
      
      if (params?.classroom) {
        schedules = schedules.filter((schedule: any) => schedule.classroom.includes(params.classroom));
      }
      
      // 模拟分页
      const page = params?.page || 1;
      const pageSize = params?.page_size || 20;
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      
      const paginatedSchedules = schedules.slice(start, end);
      
      return {
        data: {
          count: schedules.length,
          next: end < schedules.length ? `?page=${page + 1}` : null,
          previous: page > 1 ? `?page=${page - 1}` : null,
          results: paginatedSchedules
        }
      };
    } catch (error) {
      console.error('获取排课数据失败:', error);
      // 返回空数据作为后备
      return {
        data: {
          count: 0,
          next: null,
          previous: null,
          results: []
        }
      };
    }
  },
  
  getSchedule: async (id: number) => {
    try {
      const response = await fetch('/data/schedules.json');
      const data = await response.json();
      const schedule = data.schedules.find((s: any) => s.id === String(id));
      
      return {
        data: schedule || null
      };
    } catch (error) {
      console.error('获取排课详情失败:', error);
      return { data: null };
    }
  },
  
  createSchedule: async (data: any) => {
    // 模拟创建操作
    return {
      data: { ...data, id: Date.now().toString() }
    };
  },
  
  updateSchedule: async (id: number, data: any) => {
    // 模拟更新操作
    return {
      data: { ...data, id: String(id) }
    };
  },
  
  deleteSchedule: async (id: number) => {
    // 模拟删除操作
    return {
      data: { message: '删除成功' }
    };
  },
  
  checkConflicts: async (data: any) => {
    // 模拟冲突检测 - 返回无冲突
    return {
      data: {
        has_conflicts: false,
        conflicts: [],
        message: '未检测到冲突'
      }
    };
  },

  exportSchedules: async (params?: any) => {
    // 模拟导出操作
    return {
      data: new Blob(['模拟导出数据'], { type: 'text/csv' })
    };
  }
};

export default mockScheduleAPI;
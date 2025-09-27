import axios from 'axios';

// 简化版排课API - 直接返回数据
export const simpleScheduleAPI = {
  getSchedules: async (params?: any) => {
    try {
      console.log('📡 调用 simpleScheduleAPI.getSchedules:', params);
      
      // 使用相对路径获取数据文件，避免CORS问题
      const response = await fetch('/data/schedules.json');
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📊 获取到的数据:', data);
      
      let schedules = data.schedules || [];
      
      // 应用过滤
      if (params?.semester) {
        schedules = schedules.filter((s: any) => s.semester === params.semester);
      }
      if (params?.teacher) {
        schedules = schedules.filter((s: any) => s.teacher.includes(params.teacher));
      }
      
      // 模拟分页
      const page = params?.page || 1;
      const pageSize = params?.page_size || 10;
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      
      const paginatedSchedules = schedules.slice(start, end);
      
      console.log('📄 分页结果:', {
        originalCount: schedules.length,
        page, pageSize, start, end,
        paginatedCount: paginatedSchedules.length
      });
      
      // 返回兼容格式
      return {
        data: {
          count: schedules.length,
          next: end < schedules.length ? `?page=${page + 1}` : null,
          previous: page > 1 ? `?page=${page - 1}` : null,
          results: paginatedSchedules
        }
      };
      
    } catch (error) {
      console.error('❌ simpleScheduleAPI 调用失败:', error);
      // 返回空数据而不是抛出错误
      return {
        data: {
          count: 0,
          next: null,
          previous: null,
          results: []
        }
      };
    }
  }
};

export default simpleScheduleAPI;
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../index';

// 基础查询配置
const baseQuery = fetchBaseQuery({
  baseUrl: '/api/v1/',
  prepareHeaders: (headers, { getState }) => {
    // 从state中获取token
    const token = (getState() as RootState).auth.token;

    // 如果有token，添加到请求头
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }

    // 设置内容类型
    headers.set('content-type', 'application/json');

    return headers;
  },
});

// 带有重新认证的查询
const baseQueryWithReauth = async (args: any, api: any, extraOptions: any) => {
  let result = await baseQuery(args, api, extraOptions);

  // 如果返回401，尝试刷新token
  if (result.error && result.error.status === 401) {
    // 尝试刷新token
    const refreshResult = await baseQuery(
      {
        url: 'auth/refresh/',
        method: 'POST',
        body: {
          refresh: localStorage.getItem('refreshToken'),
        },
      },
      api,
      extraOptions
    );

    if (refreshResult.data) {
      // 保存新token
      const newToken = (refreshResult.data as any).access;
      localStorage.setItem('token', newToken);

      // 更新store中的token
      api.dispatch({
        type: 'auth/setCredentials',
        payload: { token: newToken },
      });

      // 重试原始请求
      result = await baseQuery(args, api, extraOptions);
    } else {
      // 刷新失败，清除认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      api.dispatch({ type: 'auth/clearCredentials' });
    }
  }

  return result;
};

// 创建API切片
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'User',
    'Course',
    'Schedule',
    'Classroom',
    'TimeSlot',
    'Conflict',
    'Analytics',
  ],
  endpoints: builder => ({
    // 认证相关
    login: builder.mutation({
      query: credentials => ({
        url: 'auth/login/',
        method: 'POST',
        body: credentials,
      }),
    }),

    logout: builder.mutation({
      query: () => ({
        url: 'auth/logout/',
        method: 'POST',
      }),
    }),

    getCurrentUser: builder.query({
      query: () => 'auth/user/',
      providesTags: ['User'],
    }),

    // 课程相关
    getCourses: builder.query({
      query: (params = {}) => ({
        url: 'courses/',
        params,
      }),
      providesTags: ['Course'],
    }),

    getCourse: builder.query({
      query: id => `courses/${id}/`,
      providesTags: (_, __, id) => [{ type: 'Course', id }],
    }),

    createCourse: builder.mutation({
      query: courseData => ({
        url: 'courses/',
        method: 'POST',
        body: courseData,
      }),
      invalidatesTags: ['Course'],
    }),

    updateCourse: builder.mutation({
      query: ({ id, ...courseData }) => ({
        url: `courses/${id}/`,
        method: 'PATCH',
        body: courseData,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Course', id }],
    }),

    deleteCourse: builder.mutation({
      query: id => ({
        url: `courses/${id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Course'],
    }),

    // 课程表相关
    getSchedules: builder.query({
      query: (params = {}) => ({
        url: 'schedules/',
        params,
      }),
      providesTags: ['Schedule'],
    }),

    getSchedule: builder.query({
      query: id => `schedules/${id}/`,
      providesTags: (_, __, id) => [{ type: 'Schedule', id }],
    }),

    createSchedule: builder.mutation({
      query: scheduleData => ({
        url: 'schedules/',
        method: 'POST',
        body: scheduleData,
      }),
      invalidatesTags: ['Schedule', 'Conflict'],
    }),

    updateSchedule: builder.mutation({
      query: ({ id, ...scheduleData }) => ({
        url: `schedules/${id}/`,
        method: 'PATCH',
        body: scheduleData,
      }),
      invalidatesTags: (_, __, { id }) => [
        { type: 'Schedule', id },
        'Conflict',
      ],
    }),

    deleteSchedule: builder.mutation({
      query: id => ({
        url: `schedules/${id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Schedule', 'Conflict'],
    }),

    // 时间段相关
    getTimeSlots: builder.query({
      query: () => 'time-slots/',
      providesTags: ['TimeSlot'],
    }),

    // 教室相关
    getClassrooms: builder.query({
      query: (params = {}) => ({
        url: 'classrooms/',
        params,
      }),
      providesTags: ['Classroom'],
    }),

    // 冲突检测
    detectConflicts: builder.query({
      query: (params = {}) => ({
        url: 'schedules/conflicts/',
        params,
      }),
      providesTags: ['Conflict'],
    }),

    // 自动排课
    autoSchedule: builder.mutation({
      query: params => ({
        url: 'schedules/auto-schedule/',
        method: 'POST',
        body: params,
      }),
      invalidatesTags: ['Schedule', 'Conflict'],
    }),

    // 数据分析
    getDashboardStats: builder.query({
      query: () => 'analytics/dashboard/',
      providesTags: ['Analytics'],
    }),

    getCourseDistribution: builder.query({
      query: (params = {}) => ({
        url: 'analytics/course-distribution/',
        params,
      }),
      providesTags: ['Analytics'],
    }),

    getClassroomUsage: builder.query({
      query: (params = {}) => ({
        url: 'analytics/classroom-usage/',
        params,
      }),
      providesTags: ['Analytics'],
    }),
  }),
});

// 导出hooks
export const {
  useLoginMutation,
  useLogoutMutation,
  useGetCurrentUserQuery,
  useGetCoursesQuery,
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useGetSchedulesQuery,
  useGetScheduleQuery,
  useCreateScheduleMutation,
  useUpdateScheduleMutation,
  useDeleteScheduleMutation,
  useGetTimeSlotsQuery,
  useGetClassroomsQuery,
  useDetectConflictsQuery,
  useAutoScheduleMutation,
  useGetDashboardStatsQuery,
  useGetCourseDistributionQuery,
  useGetClassroomUsageQuery,
} = apiSlice;

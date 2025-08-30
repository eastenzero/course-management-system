import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { Schedule, TimeSlot, Conflict } from '../../types/index';
import { scheduleAPI } from '../../api/schedules';

interface ScheduleState {
  schedules: Schedule[];
  timeSlots: TimeSlot[];
  conflicts: Conflict[];
  currentSchedule: Schedule | null;
  loading: boolean;
  error: string | null;
  selectedWeek: number;
  selectedSemester: string;
  viewMode: 'week' | 'month';
  filters: {
    teacher: string | null;
    classroom: string | null;
    course: string | null;
    status: string | null;
  };
}

// 异步thunk
export const fetchSchedules = createAsyncThunk(
  'schedules/fetchSchedules',
  async (
    params: {
      week?: number;
      semester?: string;
      teacher?: string;
      classroom?: string;
      course?: string;
    } = {},
    { rejectWithValue }
  ) => {
    try {
      const response = await scheduleAPI.getSchedules(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '获取课程表失败');
    }
  }
);

export const fetchTimeSlots = createAsyncThunk(
  'schedules/fetchTimeSlots',
  async (_, { rejectWithValue }) => {
    try {
      const response = await scheduleAPI.getTimeSlots();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '获取时间段失败');
    }
  }
);

export const createSchedule = createAsyncThunk(
  'schedules/createSchedule',
  async (scheduleData: Partial<Schedule>, { rejectWithValue }) => {
    try {
      const response = await scheduleAPI.createSchedule(scheduleData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '创建课程安排失败'
      );
    }
  }
);

export const updateSchedule = createAsyncThunk(
  'schedules/updateSchedule',
  async (
    { id, data }: { id: string | number; data: Partial<Schedule> },
    { rejectWithValue }
  ) => {
    try {
      const response = await scheduleAPI.updateSchedule(id, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '更新课程安排失败'
      );
    }
  }
);

export const deleteSchedule = createAsyncThunk(
  'schedules/deleteSchedule',
  async (id: string | number, { rejectWithValue }) => {
    try {
      await scheduleAPI.deleteSchedule(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '删除课程安排失败'
      );
    }
  }
);

export const detectConflicts = createAsyncThunk(
  'schedules/detectConflicts',
  async (
    params: { week?: number; semester?: string } = {},
    { rejectWithValue }
  ) => {
    try {
      const response = await scheduleAPI.detectConflicts(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '检测冲突失败');
    }
  }
);

export const autoSchedule = createAsyncThunk(
  'schedules/autoSchedule',
  async (
    params: {
      semester: string;
      courses: string[];
      constraints?: any;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await scheduleAPI.autoSchedule(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '自动排课失败');
    }
  }
);

// 初始状态
const initialState: ScheduleState = {
  schedules: [],
  timeSlots: [],
  conflicts: [],
  currentSchedule: null,
  loading: false,
  error: null,
  selectedWeek: 1,
  selectedSemester: '',
  viewMode: 'week',
  filters: {
    teacher: null,
    classroom: null,
    course: null,
    status: null,
  },
};

// 创建slice
const scheduleSlice = createSlice({
  name: 'schedules',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
    setCurrentSchedule: (state, action: PayloadAction<Schedule | null>) => {
      state.currentSchedule = action.payload;
    },
    setSelectedWeek: (state, action: PayloadAction<number>) => {
      state.selectedWeek = action.payload;
    },
    setSelectedSemester: (state, action: PayloadAction<string>) => {
      state.selectedSemester = action.payload;
    },
    setViewMode: (state, action: PayloadAction<'week' | 'month'>) => {
      state.viewMode = action.payload;
    },
    setFilters: (
      state,
      action: PayloadAction<Partial<ScheduleState['filters']>>
    ) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: state => {
      state.filters = {
        teacher: null,
        classroom: null,
        course: null,
        status: null,
      };
    },
    clearConflicts: state => {
      state.conflicts = [];
    },
  },
  extraReducers: builder => {
    builder
      // 获取课程表
      .addCase(fetchSchedules.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSchedules.fulfilled, (state, action) => {
        state.loading = false;
        state.schedules = action.payload;
      })
      .addCase(fetchSchedules.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取时间段
      .addCase(fetchTimeSlots.fulfilled, (state, action) => {
        state.timeSlots = action.payload;
      })
      // 创建课程安排
      .addCase(createSchedule.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSchedule.fulfilled, (state, action) => {
        state.loading = false;
        state.schedules.push(action.payload);
      })
      .addCase(createSchedule.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 更新课程安排
      .addCase(updateSchedule.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateSchedule.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.schedules.findIndex(
          schedule => schedule.id === action.payload.id
        );
        if (index !== -1) {
          state.schedules[index] = action.payload;
        }
        if (state.currentSchedule?.id === action.payload.id) {
          state.currentSchedule = action.payload;
        }
      })
      .addCase(updateSchedule.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 删除课程安排
      .addCase(deleteSchedule.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteSchedule.fulfilled, (state, action) => {
        state.loading = false;
        state.schedules = state.schedules.filter(
          schedule => schedule.id !== action.payload
        );
        if (state.currentSchedule?.id === action.payload) {
          state.currentSchedule = null;
        }
      })
      .addCase(deleteSchedule.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 检测冲突
      .addCase(detectConflicts.fulfilled, (state, action) => {
        state.conflicts = action.payload;
      })
      // 自动排课
      .addCase(autoSchedule.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(autoSchedule.fulfilled, (state, action) => {
        state.loading = false;
        state.schedules = action.payload;
      })
      .addCase(autoSchedule.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  setCurrentSchedule,
  setSelectedWeek,
  setSelectedSemester,
  setViewMode,
  setFilters,
  clearFilters,
  clearConflicts,
} = scheduleSlice.actions;

export default scheduleSlice.reducer;

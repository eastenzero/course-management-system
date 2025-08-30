import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { Course, CourseStatus } from '../../types/index';
import { courseAPI } from '../../api/courses';

interface CourseState {
  courses: Course[];
  currentCourse: Course | null;
  loading: boolean;
  error: string | null;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
  };
  filters: {
    search: string;
    status: CourseStatus | null;
    department: string | null;
    semester: string | null;
  };
}

// 异步thunk
export const fetchCourses = createAsyncThunk(
  'courses/fetchCourses',
  async (
    params: {
      page?: number;
      pageSize?: number;
      search?: string;
      status?: CourseStatus;
      department?: string;
      semester?: string;
    } = {},
    { rejectWithValue }
  ) => {
    try {
      const response = await courseAPI.getCourses(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '获取课程列表失败'
      );
    }
  }
);

export const fetchCourseById = createAsyncThunk(
  'courses/fetchCourseById',
  async (id: string | number, { rejectWithValue }) => {
    try {
      const response = await courseAPI.getCourseById(id);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '获取课程详情失败'
      );
    }
  }
);

export const createCourse = createAsyncThunk(
  'courses/createCourse',
  async (courseData: Partial<Course>, { rejectWithValue }) => {
    try {
      const response = await courseAPI.createCourse(courseData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '创建课程失败');
    }
  }
);

export const updateCourse = createAsyncThunk(
  'courses/updateCourse',
  async (
    { id, data }: { id: string | number; data: Partial<Course> },
    { rejectWithValue }
  ) => {
    try {
      const response = await courseAPI.updateCourse(id, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '更新课程失败');
    }
  }
);

export const deleteCourse = createAsyncThunk(
  'courses/deleteCourse',
  async (id: string | number, { rejectWithValue }) => {
    try {
      await courseAPI.deleteCourse(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '删除课程失败');
    }
  }
);

// 初始状态
const initialState: CourseState = {
  courses: [],
  currentCourse: null,
  loading: false,
  error: null,
  pagination: {
    current: 1,
    pageSize: 10,
    total: 0,
  },
  filters: {
    search: '',
    status: null,
    department: null,
    semester: null,
  },
};

// 创建slice
const courseSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
    setCurrentCourse: (state, action: PayloadAction<Course | null>) => {
      state.currentCourse = action.payload;
    },
    setPagination: (
      state,
      action: PayloadAction<Partial<CourseState['pagination']>>
    ) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    setFilters: (
      state,
      action: PayloadAction<Partial<CourseState['filters']>>
    ) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: state => {
      state.filters = {
        search: '',
        status: null,
        department: null,
        semester: null,
      };
    },
  },
  extraReducers: builder => {
    builder
      // 获取课程列表
      .addCase(fetchCourses.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.courses = action.payload.results;
        state.pagination.total = action.payload.count;
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取课程详情
      .addCase(fetchCourseById.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourseById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCourse = action.payload;
      })
      .addCase(fetchCourseById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 创建课程
      .addCase(createCourse.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createCourse.fulfilled, (state, action) => {
        state.loading = false;
        state.courses.unshift(action.payload);
        state.pagination.total += 1;
      })
      .addCase(createCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 更新课程
      .addCase(updateCourse.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCourse.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.courses.findIndex(
          course => course.id === action.payload.id
        );
        if (index !== -1) {
          state.courses[index] = action.payload;
        }
        if (state.currentCourse?.id === action.payload.id) {
          state.currentCourse = action.payload;
        }
      })
      .addCase(updateCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 删除课程
      .addCase(deleteCourse.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteCourse.fulfilled, (state, action) => {
        state.loading = false;
        state.courses = state.courses.filter(
          course => course.id !== action.payload
        );
        state.pagination.total -= 1;
        if (state.currentCourse?.id === action.payload) {
          state.currentCourse = null;
        }
      })
      .addCase(deleteCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  setCurrentCourse,
  setPagination,
  setFilters,
  clearFilters,
} = courseSlice.actions;

export default courseSlice.reducer;

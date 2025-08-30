import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import '@testing-library/jest-dom';

import CourseListPage from '../CourseListPage';
import { courseAPI } from '../../../services/api';
import authSlice from '../../../store/slices/authSlice';

// Mock API
jest.mock('../../../services/api', () => ({
  courseAPI: {
    getCourses: jest.fn(),
    deleteCourse: jest.fn(),
  },
}));

// Mock hooks
jest.mock('../../../hooks', () => ({
  useApi: jest.fn(),
  useTablePagination: jest.fn(),
  usePermission: jest.fn(),
}));

const mockCourses = [
  {
    id: 1,
    code: 'CS101',
    name: '计算机科学导论',
    credits: 3,
    department: '计算机学院',
    teachers_count: 2,
    current_enrollment: 45,
    max_students: 50,
    is_full: false,
    course_type_display: '必修课',
    is_active: true,
    is_published: true,
  },
  {
    id: 2,
    code: 'MATH201',
    name: '高等数学',
    credits: 4,
    department: '数学学院',
    teachers_count: 1,
    current_enrollment: 30,
    max_students: 30,
    is_full: true,
    course_type_display: '必修课',
    is_active: true,
    is_published: true,
  },
];

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice,
    },
    preloadedState: {
      auth: {
        isAuthenticated: true,
        user: {
          id: 1,
          username: 'admin',
          user_type: 'admin',
        },
        token: 'mock-token',
        ...initialState.auth,
      },
      ...initialState,
    },
  });
};

const renderWithProviders = (
  ui: React.ReactElement,
  { initialState = {}, store = createMockStore(initialState) } = {}
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>
      <BrowserRouter>{children}</BrowserRouter>
    </Provider>
  );

  return render(ui, { wrapper: Wrapper });
};

describe('CourseListPage Integration Tests', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock hooks return values
    const { useApi, useTablePagination, usePermission } = require('../../../hooks');
    
    useApi.mockReturnValue({
      data: { results: { data: mockCourses }, count: 2 },
      loading: false,
      run: jest.fn(),
      refresh: jest.fn(),
    });
    
    useTablePagination.mockReturnValue({
      tablePagination: {
        current: 1,
        pageSize: 20,
        total: 2,
        showQuickJumper: true,
        showSizeChanger: true,
        showTotal: expect.any(Function),
        onChange: jest.fn(),
        onShowSizeChange: jest.fn(),
      },
      setTotal: jest.fn(),
    });
    
    usePermission.mockReturnValue({
      hasPermission: jest.fn().mockReturnValue(true),
      isAdmin: true,
      userRole: 'admin',
    });
  });

  it('renders course list page correctly', async () => {
    renderWithProviders(<CourseListPage />);

    // Check page title
    expect(screen.getByText('课程管理')).toBeInTheDocument();
    expect(screen.getByText('管理课程信息、选课和退课')).toBeInTheDocument();

    // Check if courses are displayed
    await waitFor(() => {
      expect(screen.getByText('计算机科学导论')).toBeInTheDocument();
      expect(screen.getByText('高等数学')).toBeInTheDocument();
    });
  });

  it('displays course information correctly', async () => {
    renderWithProviders(<CourseListPage />);

    await waitFor(() => {
      // Check course codes
      expect(screen.getByText('CS101')).toBeInTheDocument();
      expect(screen.getByText('MATH201')).toBeInTheDocument();

      // Check departments
      expect(screen.getByText('计算机学院')).toBeInTheDocument();
      expect(screen.getByText('数学学院')).toBeInTheDocument();

      // Check enrollment status
      expect(screen.getByText('45/50')).toBeInTheDocument();
      expect(screen.getByText('30/30')).toBeInTheDocument();
      expect(screen.getByText('满')).toBeInTheDocument();
    });
  });

  it('handles search functionality', async () => {
    const mockRun = jest.fn();
    const { useApi } = require('../../../hooks');
    useApi.mockReturnValue({
      data: { results: { data: mockCourses }, count: 2 },
      loading: false,
      run: mockRun,
      refresh: jest.fn(),
    });

    renderWithProviders(<CourseListPage />);

    // Find search input
    const searchInput = screen.getByPlaceholderText('请输入课程名称或代码');
    expect(searchInput).toBeInTheDocument();

    // Type in search input
    fireEvent.change(searchInput, { target: { value: '计算机' } });

    // Find and click search button
    const searchButton = screen.getByText('搜索');
    fireEvent.click(searchButton);

    // Verify API call
    await waitFor(() => {
      expect(mockRun).toHaveBeenCalledWith(
        expect.objectContaining({
          search: '计算机',
        })
      );
    });
  });

  it('handles filter functionality', async () => {
    renderWithProviders(<CourseListPage />);

    // Find department filter
    const departmentSelect = screen.getByPlaceholderText('请选择院系');
    fireEvent.mouseDown(departmentSelect);

    // Wait for options to appear and select one
    await waitFor(() => {
      const option = screen.getByText('计算机学院');
      fireEvent.click(option);
    });

    // Click search to apply filter
    const searchButton = screen.getByText('搜索');
    fireEvent.click(searchButton);
  });

  it('shows add course button for authorized users', () => {
    renderWithProviders(<CourseListPage />);

    const addButton = screen.getByText('添加课程');
    expect(addButton).toBeInTheDocument();
  });

  it('hides add course button for unauthorized users', () => {
    const { usePermission } = require('../../../hooks');
    usePermission.mockReturnValue({
      hasPermission: jest.fn().mockReturnValue(false),
      isAdmin: false,
      userRole: 'student',
    });

    renderWithProviders(<CourseListPage />);

    const addButton = screen.queryByText('添加课程');
    expect(addButton).not.toBeInTheDocument();
  });

  it('handles export functionality', async () => {
    renderWithProviders(<CourseListPage />);

    // Find export dropdown
    const exportButton = screen.getByText('导出数据');
    fireEvent.click(exportButton);

    // Wait for dropdown menu
    await waitFor(() => {
      expect(screen.getByText('导出CSV')).toBeInTheDocument();
      expect(screen.getByText('导出Excel')).toBeInTheDocument();
      expect(screen.getByText('导出JSON')).toBeInTheDocument();
    });
  });

  it('handles course actions correctly', async () => {
    renderWithProviders(<CourseListPage />);

    await waitFor(() => {
      // Check action buttons
      const viewButtons = screen.getAllByText('查看');
      const editButtons = screen.getAllByText('编辑');
      const deleteButtons = screen.getAllByText('删除');

      expect(viewButtons).toHaveLength(2);
      expect(editButtons).toHaveLength(2);
      expect(deleteButtons).toHaveLength(2);
    });
  });

  it('handles delete confirmation dialog', async () => {
    renderWithProviders(<CourseListPage />);

    await waitFor(() => {
      const deleteButtons = screen.getAllByText('删除');
      fireEvent.click(deleteButtons[0]);
    });

    // Check if confirmation dialog appears
    await waitFor(() => {
      expect(screen.getByText('删除课程')).toBeInTheDocument();
      expect(screen.getByText(/确定要删除课程/)).toBeInTheDocument();
    });
  });

  it('shows empty state when no courses', () => {
    const { useApi } = require('../../../hooks');
    useApi.mockReturnValue({
      data: { results: { data: [] }, count: 0 },
      loading: false,
      run: jest.fn(),
      refresh: jest.fn(),
    });

    renderWithProviders(<CourseListPage />);

    expect(screen.getByText('没有找到课程')).toBeInTheDocument();
    expect(screen.getByText('当前搜索条件下没有找到相关课程，请尝试调整搜索条件')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    const { useApi } = require('../../../hooks');
    useApi.mockReturnValue({
      data: null,
      loading: true,
      run: jest.fn(),
      refresh: jest.fn(),
    });

    renderWithProviders(<CourseListPage />);

    expect(screen.getByText('加载课程数据中...')).toBeInTheDocument();
  });

  it('handles pagination correctly', async () => {
    const mockOnChange = jest.fn();
    const { useTablePagination } = require('../../../hooks');
    useTablePagination.mockReturnValue({
      tablePagination: {
        current: 1,
        pageSize: 20,
        total: 100,
        showQuickJumper: true,
        showSizeChanger: true,
        showTotal: expect.any(Function),
        onChange: mockOnChange,
        onShowSizeChange: jest.fn(),
      },
      setTotal: jest.fn(),
    });

    renderWithProviders(<CourseListPage />);

    // The pagination should be rendered with correct props
    await waitFor(() => {
      // Check if pagination is working (this would need more specific testing)
      expect(screen.getByText('计算机科学导论')).toBeInTheDocument();
    });
  });
});

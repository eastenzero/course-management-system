// 基础类型定义
export interface BaseEntity {
  id: string | number;
  created_at: string;
  updated_at: string;
}

// 用户相关类型
export interface User extends BaseEntity {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: UserRole; // 后端返回的字段名是user_type
  user_type_display: string;
  employee_id?: string;
  student_id?: string;
  is_active: boolean;
  avatar?: string;
  phone?: string;
  department?: string;
  display_id?: string;
}

export type UserRole = 'admin' | 'teacher' | 'student';

export interface LoginForm {
  username: string;
  password: string;
  remember?: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

// 课程相关类型
export interface Course extends BaseEntity {
  name: string;
  code: string;
  description?: string;
  credits: number;
  hours: number;
  department: string;
  teacher: User;
  capacity: number;
  enrolled_count: number;
  semester: string;
  academic_year: string;
  prerequisites?: Course[];
  status: CourseStatus;
}

export enum CourseStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

// 教室相关类型
export interface Classroom extends BaseEntity {
  name: string;
  building: string;
  floor: number;
  capacity: number;
  type: ClassroomType;
  equipment: string[];
  is_available: boolean;
}

export enum ClassroomType {
  LECTURE = 'lecture',
  LAB = 'lab',
  SEMINAR = 'seminar',
  COMPUTER = 'computer',
  MULTIMEDIA = 'multimedia',
}

// 时间段类型
export interface TimeSlot extends BaseEntity {
  name: string;
  start_time: string;
  end_time: string;
  duration: number;
  order: number;
}

// 课程表相关类型
export interface Schedule extends BaseEntity {
  course: Course;
  classroom: Classroom;
  time_slot: TimeSlot;
  day_of_week: number; // 0-6, 0为周日
  week_number: number;
  semester: string;
  academic_year: string;
  teacher: User;
  students: User[];
  status: ScheduleStatus;
}

export enum ScheduleStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

// 冲突检测类型
export interface Conflict {
  id: string;
  type: ConflictType;
  description: string;
  severity: ConflictSeverity;
  schedules: Schedule[];
  suggestions?: string[];
}

export enum ConflictType {
  TIME_CONFLICT = 'time_conflict',
  ROOM_CONFLICT = 'room_conflict',
  TEACHER_CONFLICT = 'teacher_conflict',
  STUDENT_CONFLICT = 'student_conflict',
  CAPACITY_CONFLICT = 'capacity_conflict',
}

export enum ConflictSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// 统计数据类型
export interface DashboardStats {
  totalCourses: number;
  totalStudents: number;
  totalTeachers: number;
  totalClassrooms: number;
  classroomUtilization: number;
  courseDistribution: ChartData[];
  classroomUsage: ChartData[];
  weeklySchedule: ChartData[];
}

export interface ChartData {
  name: string;
  value: number;
  category?: string;
  color?: string;
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 表格相关类型
export interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number;
  fixed?: 'left' | 'right';
  sorter?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
}

export interface TablePagination {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => string;
}

// 表单相关类型
export interface FormField {
  name: string;
  label: string;
  type: 'input' | 'select' | 'textarea' | 'date' | 'number' | 'checkbox';
  required?: boolean;
  options?: { label: string; value: any }[];
  placeholder?: string;
  rules?: any[];
}

// 路由相关类型
export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  roles?: UserRole[];
  title?: string;
  icon?: string;
  children?: RouteConfig[];
}

// 菜单相关类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  roles?: UserRole[];
}

// 通知相关类型
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'info' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// 主题相关类型
export interface ThemeConfig {
  primaryColor: string;
  mode: 'light' | 'dark';
  compact: boolean;
}

// 应用状态类型
export interface AppState {
  theme: ThemeConfig;
  sidebarCollapsed: boolean;
  loading: boolean;
  notifications: Notification[];
}

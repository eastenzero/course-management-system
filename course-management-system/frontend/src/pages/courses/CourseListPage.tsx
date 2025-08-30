import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Table,
  Button,
  Space,
  Card,
  Tag,
  message,
  Popconfirm,
  Dropdown,
  Menu,
  Select,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ExportOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { courseAPI } from '../../services/api';
import {
  SearchForm,
  EmptyState,
  LoadingSpinner,
  ConfirmDialog
} from '../../components/common';
import {
  useApi,
  useTablePagination,
  useDebouncedInput,
  usePermission
} from '../../hooks';
import {
  formatCourseType,
  formatStatus,
  exportCourses
} from '../../utils';
import { useAppSelector } from '../../store/index';

const { Title } = Typography;
const { Option } = Select;

interface Course {
  id: number;
  name: string;
  code: string;
  credits: number;
  department: string;
  course_type: string;
  course_type_display: string;
  hours: number;
  semester: string;
  max_students: number;
  current_enrollment: number;
  is_full: boolean;
  teachers_count: number;
  is_active: boolean;
  is_published: boolean;
}

const CourseListPage: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermission } = usePermission();
  const { isAuthenticated, user } = useAppSelector(state => state.auth);
  const [searchParams, setSearchParams] = useState<any>({});
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  const [deletingCourse, setDeletingCourse] = useState<Course | null>(null);

  // 使用自定义hooks
  const { tablePagination, setTotal } = useTablePagination({
    defaultPageSize: 20,
  });

  const {
    data: coursesData,
    loading,
    run: fetchCourses,
    refresh
  } = useApi(courseAPI.getCourses, {
    immediate: true, // 改为true，自动加载数据
    onSuccess: (data) => {
      setTotal(data?.count || 0);
    },
    showError: true,
    errorMessage: '获取课程列表失败',
  });

  // 只有在用户已认证时才获取数据
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchCourses({
        page: tablePagination.current,
        page_size: tablePagination.pageSize,
        ...searchParams,
      });
    }
  }, [isAuthenticated, user, tablePagination.current, tablePagination.pageSize, searchParams]);

  const courses = coursesData?.results || [];

  // 搜索表单配置
  const searchFields = [
    {
      name: 'search',
      label: '课程名称/代码',
      type: 'input' as const,
      placeholder: '请输入课程名称或代码',
      span: 8,
    },
    {
      name: 'department',
      label: '院系',
      type: 'select' as const,
      placeholder: '请选择院系',
      options: [
        { label: '计算机学院', value: '计算机学院' },
        { label: '数学学院', value: '数学学院' },
        { label: '物理学院', value: '物理学院' },
        { label: '化学学院', value: '化学学院' },
      ],
      span: 6,
    },
    {
      name: 'course_type',
      label: '课程类型',
      type: 'select' as const,
      placeholder: '请选择课程类型',
      options: [
        { label: '必修课', value: 'required' },
        { label: '选修课', value: 'elective' },
        { label: '公共课', value: 'public' },
      ],
      span: 6,
    },
  ];

  // 搜索处理
  const handleSearch = (values: any) => {
    setSearchParams(values);
    fetchCourses({
      page: 1,
      page_size: tablePagination.pageSize,
      ...values,
    });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchParams({});
    fetchCourses({
      page: 1,
      page_size: tablePagination.pageSize,
    });
  };

  // 删除课程
  const handleDeleteClick = (course: Course) => {
    setDeletingCourse(course);
    setDeleteDialogVisible(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingCourse) return;

    try {
      await courseAPI.deleteCourse(deletingCourse.id);
      message.success('课程删除成功');
      refresh();
      setDeleteDialogVisible(false);
      setDeletingCourse(null);
    } catch (error) {
      console.error('删除课程失败:', error);
      message.error('删除课程失败');
    }
  };

  // 导出功能
  const handleExport = (format: 'csv' | 'excel' | 'json') => {
    exportCourses(courses, format);
  };

  const exportMenu = (
    <Menu>
      <Menu.Item key="csv" onClick={() => handleExport('csv')}>
        导出CSV
      </Menu.Item>
      <Menu.Item key="excel" onClick={() => handleExport('excel')}>
        导出Excel
      </Menu.Item>
      <Menu.Item key="json" onClick={() => handleExport('json')}>
        导出JSON
      </Menu.Item>
    </Menu>
  );

  const columns = [
    {
      title: '课程代码',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: '课程名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '学分',
      dataIndex: 'credits',
      key: 'credits',
      width: 80,
      align: 'center' as const,
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
      render: (department: string) => department || '未分配',
    },
    {
      title: '授课教师',
      dataIndex: 'teachers_count',
      key: 'teachers_count',
      width: 120,
      render: (count: number) => `${count}位教师`,
    },
    {
      title: '容量/已选',
      key: 'enrollment',
      width: 120,
      render: (record: Course) => (
        <span style={{ color: record.is_full ? '#ff4d4f' : '#52c41a' }}>
          {record.current_enrollment}/{record.max_students}
          {record.is_full && <Tag color="red" size="small" style={{ marginLeft: 4 }}>满</Tag>}
        </span>
      ),
    },
    {
      title: '课程类型',
      dataIndex: 'course_type_display',
      key: 'course_type_display',
      width: 100,
      render: (type: string) => (
        <Tag color={type === '必修课' ? 'blue' : type === '选修课' ? 'green' : 'orange'}>
          {formatCourseType(type)}
        </Tag>
      ),
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (record: Course) => (
        <Tag color={record.is_active && record.is_published ? 'green' : 'red'}>
          {formatStatus(record.is_active && record.is_published)}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (record: Course) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/courses/${record.id}`)}
          >
            查看
          </Button>
          {hasPermission('course.edit') && (
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => navigate(`/courses/${record.id}/edit`)}
            >
              编辑
            </Button>
          )}
          {hasPermission('course.delete') && (
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteClick(record)}
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="course-list-page">
      <div className="page-header">
        <Title level={2}>课程管理</Title>
        <p>管理课程信息、选课和退课</p>
      </div>

      <Card>
        {/* 搜索表单 */}
        <SearchForm
          fields={searchFields}
          onSearch={handleSearch}
          onReset={handleReset}
          loading={loading}
          style={{ marginBottom: 16 }}
        />

        {/* 操作按钮 */}
        <div style={{ marginBottom: 16, textAlign: 'right' }}>
          <Space>
            <Dropdown overlay={exportMenu} disabled={!courses.length}>
              <Button icon={<ExportOutlined />}>
                导出数据 <DownOutlined />
              </Button>
            </Dropdown>
            {hasPermission('course.create') && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/courses/create')}
              >
                添加课程
              </Button>
            )}
          </Space>
        </div>

        {/* 数据表格 */}
        {loading ? (
          <LoadingSpinner tip="加载课程数据中..." />
        ) : courses.length > 0 ? (
          <Table
            columns={columns}
            dataSource={courses}
            rowKey="id"
            pagination={{
              ...tablePagination,
              onChange: (page, pageSize) => {
                fetchCourses({
                  page,
                  page_size: pageSize,
                  ...searchParams,
                });
              },
            }}
          />
        ) : (
          <EmptyState
            type="search"
            title="没有找到课程"
            description="当前搜索条件下没有找到相关课程，请尝试调整搜索条件"
            primaryAction={
              hasPermission('course.create') ? {
                text: '添加课程',
                onClick: () => navigate('/courses/create'),
                icon: <PlusOutlined />,
              } : undefined
            }
            secondaryAction={{
              text: '重置搜索',
              onClick: handleReset,
            }}
          />
        )}
      </Card>

      {/* 删除确认对话框 */}
      <ConfirmDialog
        visible={deleteDialogVisible}
        onClose={() => setDeleteDialogVisible(false)}
        onConfirm={handleDeleteConfirm}
        title="删除课程"
        content={
          deletingCourse ? (
            <div>
              <p>确定要删除课程 <strong>{deletingCourse.name}</strong> 吗？</p>
              <p style={{ color: '#999', fontSize: '12px' }}>
                删除后将无法恢复，请谨慎操作。
              </p>
            </div>
          ) : null
        }
        type="warning"
        okText="删除"
        okType="danger"
      />
    </div>
  );
};

export default CourseListPage;

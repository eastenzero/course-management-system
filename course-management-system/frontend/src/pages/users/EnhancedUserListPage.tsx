import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Table,
  Button,
  Space,
  Card,
  Tag,
  Avatar,
  Switch,
  Dropdown,
  Menu,
  message,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  UserOutlined,
  ExportOutlined,
  DownOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { userAPI } from '../../services/api';
import {
  SearchForm,
  EmptyState,
  LoadingSpinner,
  ConfirmDialog,
  FilterPanel
} from '../../components/common';
import {
  useApi,
  useTablePagination,
  usePermission
} from '../../hooks';
import {
  formatUserType,
  formatStatus,
  formatTime,
  exportUsers
} from '../../utils';
import { useAppSelector } from '../../store/index';

const { Title } = Typography;

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'admin' | 'teacher' | 'student';
  user_type_display: string;
  employee_id?: string;
  student_id?: string;
  is_active: boolean;
  avatar?: string;
  phone?: string;
  department?: string;
  date_joined: string;
  display_id?: string;
}

const EnhancedUserListPage: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermission } = usePermission();
  const { isAuthenticated, user } = useAppSelector(state => state.auth);
  const [searchParams, setSearchParams] = useState<any>({});
  const [filterParams, setFilterParams] = useState<any>({});
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  const [deletingUser, setDeletingUser] = useState<User | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // 使用自定义hooks
  const { tablePagination, setTotal } = useTablePagination({
    defaultPageSize: 20,
  });

  const {
    data: usersData,
    loading,
    run: fetchUsers,
    refresh
  } = useApi(userAPI.getUsers, {
    immediate: true, // 改为true，自动加载数据
    onSuccess: (data) => {
      setTotal(data?.count || 0);
    },
    showError: true,
    errorMessage: '获取用户列表失败',
  });

  const users = usersData?.results || [];

  // 只有在用户已认证时才获取数据
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchUsers({
        page: tablePagination.current,
        page_size: tablePagination.pageSize,
        ...searchParams,
        ...filterParams,
      });
    }
  }, [isAuthenticated, user, tablePagination.current, tablePagination.pageSize, searchParams, filterParams]);

  // 搜索表单配置
  const searchFields = [
    {
      name: 'search',
      label: '用户名/邮箱',
      type: 'input' as const,
      placeholder: '请输入用户名或邮箱',
      span: 8,
    },
    {
      name: 'user_type',
      label: '用户类型',
      type: 'select' as const,
      placeholder: '请选择用户类型',
      options: [
        { label: '管理员', value: 'admin' },
        { label: '教师', value: 'teacher' },
        { label: '学生', value: 'student' },
      ],
      span: 6,
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
      ],
      span: 6,
    },
  ];

  // 过滤器配置
  const filterConfigs = [
    {
      name: 'is_active',
      title: '账户状态',
      type: 'radio' as const,
      options: [
        { label: '全部', value: '' },
        { label: '启用', value: 'true' },
        { label: '禁用', value: 'false' },
      ],
    },
    {
      name: 'has_avatar',
      title: '头像状态',
      type: 'checkbox' as const,
      options: [
        { label: '已设置头像', value: 'true' },
        { label: '未设置头像', value: 'false' },
      ],
    },
  ];

  // 搜索处理
  const handleSearch = (values: any) => {
    setSearchParams(values);
    fetchUsers({
      page: 1,
      page_size: tablePagination.pageSize,
      ...values,
      ...filterParams,
    });
  };

  // 过滤处理
  const handleFilter = (values: any) => {
    setFilterParams(values);
    fetchUsers({
      page: 1,
      page_size: tablePagination.pageSize,
      ...searchParams,
      ...values,
    });
  };

  // 重置
  const handleReset = () => {
    setSearchParams({});
    setFilterParams({});
    fetchUsers({
      page: 1,
      page_size: tablePagination.pageSize,
    });
  };

  // 删除用户
  const handleDeleteClick = (user: User) => {
    setDeletingUser(user);
    setDeleteDialogVisible(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingUser) return;
    
    try {
      await userAPI.deleteUser(deletingUser.id);
      message.success('用户删除成功');
      refresh();
      setDeleteDialogVisible(false);
      setDeletingUser(null);
    } catch (error) {
      console.error('删除用户失败:', error);
      message.error('删除用户失败');
    }
  };

  // 切换用户状态
  const handleToggleStatus = async (user: User, checked: boolean) => {
    try {
      await userAPI.updateUser(user.id, { is_active: checked });
      message.success(`用户${checked ? '启用' : '禁用'}成功`);
      refresh();
    } catch (error) {
      message.error(`用户状态更新失败`);
    }
  };

  // 导出功能
  const handleExport = (format: 'csv' | 'excel' | 'json') => {
    exportUsers(users, format);
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
      title: '用户',
      key: 'user',
      width: 200,
      render: (record: User) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Avatar 
            src={record.avatar} 
            icon={<UserOutlined />}
            size="small"
          />
          <div>
            <div style={{ fontWeight: 500 }}>
              {record.first_name} {record.last_name}
            </div>
            <div style={{ fontSize: '12px', color: '#999' }}>
              @{record.username}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '用户类型',
      dataIndex: 'user_type_display',
      key: 'user_type_display',
      width: 100,
      render: (type: string) => (
        <Tag color={type === '管理员' ? 'red' : type === '教师' ? 'blue' : 'green'}>
          {formatUserType(type)}
        </Tag>
      ),
    },
    {
      title: '工号/学号',
      key: 'id_number',
      width: 120,
      render: (record: User) => record.employee_id || record.student_id || '-',
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
      render: (department: string) => department || '未分配',
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (record: User) => (
        <Switch
          checked={record.is_active}
          onChange={(checked) => handleToggleStatus(record, checked)}
          disabled={!hasPermission('user.edit')}
          size="small"
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'date_joined',
      key: 'date_joined',
      width: 150,
      render: (date: string) => formatTime(date, 'YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (record: User) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/users/${record.id}`)}
          >
            查看
          </Button>
          {hasPermission('user.edit') && (
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => navigate(`/users/${record.id}/edit`)}
            >
              编辑
            </Button>
          )}
          {hasPermission('user.delete') && (
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
    <div className="user-list-page">
      <div className="page-header">
        <Title level={2}>用户管理</Title>
        <p>管理系统用户信息和权限</p>
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        {/* 侧边过滤器 */}
        {showFilters && (
          <div style={{ width: 280, flexShrink: 0 }}>
            <FilterPanel
              filters={filterConfigs}
              onChange={handleFilter}
              title="筛选条件"
            />
          </div>
        )}

        {/* 主内容区 */}
        <div style={{ flex: 1 }}>
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
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                icon={<FilterOutlined />}
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? '隐藏筛选' : '显示筛选'}
              </Button>
              
              <Space>
                <Dropdown overlay={exportMenu} disabled={!users.length}>
                  <Button icon={<ExportOutlined />}>
                    导出数据 <DownOutlined />
                  </Button>
                </Dropdown>
                {hasPermission('user.create') && (
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => navigate('/users/create')}
                  >
                    添加用户
                  </Button>
                )}
              </Space>
            </div>

            {/* 数据表格 */}
            {loading ? (
              <LoadingSpinner tip="加载用户数据中..." />
            ) : users.length > 0 ? (
              <Table
                columns={columns}
                dataSource={users}
                rowKey="id"
                pagination={{
                  ...tablePagination,
                  onChange: (page, pageSize) => {
                    fetchUsers({
                      page,
                      page_size: pageSize,
                      ...searchParams,
                      ...filterParams,
                    });
                  },
                }}
              />
            ) : (
              <EmptyState
                type="search"
                title="没有找到用户"
                description="当前搜索条件下没有找到相关用户，请尝试调整搜索条件"
                primaryAction={
                  hasPermission('user.create') ? {
                    text: '添加用户',
                    onClick: () => navigate('/users/create'),
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
        </div>
      </div>

      {/* 删除确认对话框 */}
      <ConfirmDialog
        visible={deleteDialogVisible}
        onClose={() => setDeleteDialogVisible(false)}
        onConfirm={handleDeleteConfirm}
        title="删除用户"
        content={
          deletingUser ? (
            <div>
              <p>确定要删除用户 <strong>{deletingUser.first_name} {deletingUser.last_name}</strong> 吗？</p>
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

export default EnhancedUserListPage;

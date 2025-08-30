import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Table,
  Button,
  Space,
  Card,
  Input,
  Select,
  Tag,
  message,
  Popconfirm,
  Row,
  Col,
  Avatar,
  Switch,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  EyeOutlined,
  UserOutlined,
  MailOutlined,
  PhoneOutlined,
} from '@ant-design/icons';
import { userAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

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

const UserListPage: React.FC = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedUserType, setSelectedUserType] = useState<string>('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 获取用户数据
  const fetchUsers = async (page = 1, pageSize = 20, search = '', userType = '', department = '') => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (search) {
        params.search = search;
      }

      if (userType) {
        params.user_type = userType;
      }

      if (department) {
        params.department = department;
      }

      const response = await userAPI.getUsers(params);

      if (response.data && response.data.results) {
        setUsers(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      console.error('获取用户列表失败:', error);
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // 搜索处理
  const handleSearch = () => {
    fetchUsers(1, pagination.pageSize, searchText, selectedUserType, selectedDepartment);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setSelectedUserType('');
    setSelectedDepartment('');
    fetchUsers(1, pagination.pageSize);
  };

  const getUserTypeColor = (userType: string): string => {
    const colorMap = {
      admin: 'red',
      teacher: 'blue',
      student: 'green',
    };
    return colorMap[userType as keyof typeof colorMap] || 'default';
  };

  const columns = [
    {
      title: '用户信息',
      key: 'userInfo',
      width: 200,
      render: (record: User) => (
        <Space>
          <Avatar
            src={record.avatar}
            icon={<UserOutlined />}
            size="large"
          />
          <div>
            <div style={{ fontWeight: 'bold' }}>
              {record.last_name}{record.first_name}
            </div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              @{record.username}
            </div>
          </div>
        </Space>
      ),
    },
    {
      title: '用户类型',
      dataIndex: 'user_type_display',
      key: 'user_type',
      width: 100,
      render: (userTypeDisplay: string, record: User) => (
        <Tag color={getUserTypeColor(record.user_type)}>
          {userTypeDisplay}
        </Tag>
      ),
    },
    {
      title: '工号/学号',
      key: 'id_number',
      width: 120,
      render: (record: User) => (
        <span>
          {record.employee_id || record.student_id || record.display_id || '-'}
        </span>
      ),
    },
    {
      title: '联系方式',
      key: 'contact',
      width: 200,
      render: (record: User) => (
        <div>
          <div style={{ marginBottom: '4px' }}>
            <MailOutlined style={{ marginRight: '4px', color: '#666' }} />
            <span style={{ fontSize: '12px' }}>{record.email}</span>
          </div>
          {record.phone && (
            <div>
              <PhoneOutlined style={{ marginRight: '4px', color: '#666' }} />
              <span style={{ fontSize: '12px' }}>{record.phone}</span>
            </div>
          )}
        </div>
      ),
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
      render: (department: string) => department || '-',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean, record: User) => (
        <Switch
          checked={isActive}
          onChange={(checked) => handleToggleStatus(record.id, checked)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'date_joined',
      key: 'date_joined',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString(),
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
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/users/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个用户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleDelete = async (id: number) => {
    try {
      await userAPI.deleteUser(id);
      message.success('用户删除成功');
      // 重新获取当前页数据
      fetchUsers(pagination.current, pagination.pageSize, searchText, selectedUserType, selectedDepartment);
    } catch (error) {
      console.error('删除用户失败:', error);
      message.error('删除用户失败');
    }
  };

  const handleToggleStatus = async (id: number, isActive: boolean) => {
    try {
      await userAPI.updateUser(id, { is_active: isActive });
      message.success(`用户${isActive ? '启用' : '禁用'}成功`);
      // 重新获取当前页数据
      fetchUsers(pagination.current, pagination.pageSize, searchText, selectedUserType, selectedDepartment);
    } catch (error) {
      console.error('更新用户状态失败:', error);
      message.error('更新用户状态失败');
    }
  };

  // 获取院系列表用于筛选
  const departments = Array.from(new Set(users.map(user => user.department).filter(Boolean)));
  const userTypes = [
    { value: 'admin', label: '管理员' },
    { value: 'teacher', label: '教师' },
    { value: 'student', label: '学生' },
  ];

  return (
    <div className="user-list-page">
      <div className="page-header">
        <Title level={2}>用户管理</Title>
        <p>管理系统用户信息和权限</p>
      </div>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8} md={6}>
            <Input
              placeholder="搜索用户名、姓名、邮箱"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
            />
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="选择用户类型"
              style={{ width: '100%' }}
              value={selectedUserType}
              onChange={setSelectedUserType}
              allowClear
            >
              {userTypes.map(type => (
                <Option key={type.value} value={type.value}>{type.label}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="选择院系"
              style={{ width: '100%' }}
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              allowClear
            >
              {departments.map(dept => (
                <Option key={dept} value={dept}>{dept || '未分配'}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={24} md={10} style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={handleSearch}>搜索</Button>
              <Button onClick={handleReset}>重置</Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/users/create')}
              >
                添加用户
              </Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个用户`,
            onChange: (page, pageSize) => {
              fetchUsers(page, pageSize, searchText, selectedUserType, selectedDepartment);
            },
            onShowSizeChange: (current, size) => {
              fetchUsers(1, size, searchText, selectedUserType, selectedDepartment);
            },
          }}
        />
      </Card>
    </div>
  );
};

export default UserListPage;

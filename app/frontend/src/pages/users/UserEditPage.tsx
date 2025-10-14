import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Form,
  Input,
  Select,
  Button,
  Row,
  Col,
  message,
  Space,
  Switch,
  Upload,
  Avatar,
  Spin,
} from 'antd';
import { 
  ArrowLeftOutlined, 
  SaveOutlined, 
  UserOutlined,
  UploadOutlined 
} from '@ant-design/icons';
import { userAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  userType: 'admin' | 'teacher' | 'student';
  employeeId?: string;
  studentId?: string;
  isActive: boolean;
  avatar?: string;
  phone?: string;
  department?: string;
}

interface UserFormData {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  userType: 'admin' | 'teacher' | 'student';
  employeeId?: string;
  studentId?: string;
  isActive: boolean;
  phone?: string;
  department?: string;
}

const UserEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // 模拟API调用获取用户详情
    const fetchUserDetail = async () => {
      try {
        setLoading(true);
        
        // 模拟数据
        const mockUser: User = {
          id: id || '1',
          username: 'zhang.prof',
          email: 'zhang@school.edu',
          firstName: '教授',
          lastName: '张',
          userType: 'teacher',
          employeeId: 'EMP002',
          isActive: true,
          phone: '13800138002',
          department: '数学系',
        };

        setUser(mockUser);
        form.setFieldsValue(mockUser);
      } catch (error) {
        message.error('获取用户详情失败');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchUserDetail();
    }
  }, [id, form]);

  const userTypeOptions = [
    { value: 'admin', label: '管理员' },
    { value: 'teacher', label: '教师' },
    { value: 'student', label: '学生' },
  ];

  const departmentOptions = [
    { value: '计算机系', label: '计算机系' },
    { value: '数学系', label: '数学系' },
    { value: '外语系', label: '外语系' },
    { value: '物理系', label: '物理系' },
    { value: '化学系', label: '化学系' },
    { value: '信息中心', label: '信息中心' },
    { value: '教务处', label: '教务处' },
  ];

  const handleSubmit = async (values: UserFormData) => {
    try {
      setSubmitting(true);
      
      // 调用API更新用户
      await userAPI.updateUser(parseInt(id!), values);
      
      message.success('用户更新成功');
      navigate(`/users/${id}`);
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '更新失败，请重试';
      message.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate(`/users/${id}`);
  };

  const handleUserTypeChange = (userType: string) => {
    // 根据用户类型清空相关字段
    if (userType === 'student') {
      form.setFieldsValue({ employeeId: undefined });
    } else {
      form.setFieldsValue({ studentId: undefined });
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ minHeight: '200px' }} />
        </Spin>
      </div>
    );
  }

  if (!user) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>用户不存在</Title>
        <Button onClick={() => navigate('/users/list')}>
          返回用户列表
        </Button>
      </div>
    );
  }

  return (
    <div className="user-edit-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleCancel}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>编辑用户</Title>
        </Space>
        <p>修改用户信息和权限设置</p>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          {/* 头像上传 */}
          <Row justify="center" style={{ marginBottom: 24 }}>
            <Col>
              <Form.Item name="avatar" label="用户头像">
                <Upload
                  name="avatar"
                  listType="picture-card"
                  className="avatar-uploader"
                  showUploadList={false}
                  beforeUpload={() => false} // 阻止自动上传
                >
                  <div>
                    <Avatar 
                      size={80} 
                      src={user.avatar}
                      icon={<UserOutlined />} 
                    />
                    <div style={{ marginTop: 8 }}>
                      <UploadOutlined /> 更换头像
                    </div>
                  </div>
                </Upload>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, max: 20, message: '用户名长度为3-20个字符' },
                  { pattern: /^[a-zA-Z0-9._]+$/, message: '只能包含字母、数字、点和下划线' }
                ]}
              >
                <Input placeholder="如：zhang.prof" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="firstName"
                label="名"
                rules={[
                  { required: true, message: '请输入名' },
                  { max: 10, message: '名不能超过10个字符' }
                ]}
              >
                <Input placeholder="如：教授" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="lastName"
                label="姓"
                rules={[
                  { required: true, message: '请输入姓' },
                  { max: 10, message: '姓不能超过10个字符' }
                ]}
              >
                <Input placeholder="如：张" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="email"
                label="邮箱"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="如：zhang@school.edu" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="phone"
                label="手机号"
                rules={[
                  { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                ]}
              >
                <Input placeholder="如：13800138000" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="userType"
                label="用户类型"
                rules={[{ required: true, message: '请选择用户类型' }]}
              >
                <Select 
                  placeholder="选择用户类型"
                  onChange={handleUserTypeChange}
                >
                  {userTypeOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="department"
                label="院系/部门"
                rules={[{ required: true, message: '请选择院系/部门' }]}
              >
                <Select placeholder="选择院系/部门">
                  {departmentOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="isActive"
                label="账户状态"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="启用" 
                  unCheckedChildren="禁用" 
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => 
                  prevValues.userType !== currentValues.userType
                }
              >
                {({ getFieldValue }) => {
                  const userType = getFieldValue('userType');
                  if (userType === 'student') {
                    return (
                      <Form.Item
                        name="studentId"
                        label="学号"
                        rules={[
                          { required: true, message: '请输入学号' },
                          { pattern: /^STU\d{7}$/, message: '格式：STU+7位数字，如STU2024001' }
                        ]}
                      >
                        <Input placeholder="如：STU2024001" />
                      </Form.Item>
                    );
                  } else {
                    return (
                      <Form.Item
                        name="employeeId"
                        label="工号"
                        rules={[
                          { required: true, message: '请输入工号' },
                          { pattern: /^EMP\d{3}$/, message: '格式：EMP+3位数字，如EMP001' }
                        ]}
                      >
                        <Input placeholder="如：EMP001" />
                      </Form.Item>
                    );
                  }
                }}
              </Form.Item>
            </Col>
          </Row>

          <div style={{ 
            background: '#fff7e6', 
            border: '1px solid #ffd591', 
            borderRadius: '6px', 
            padding: '12px', 
            marginBottom: '16px' 
          }}>
            <strong>注意：</strong>修改用户类型或工号/学号可能会影响用户的权限和关联数据。
          </div>

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={submitting}
                icon={<SaveOutlined />}
              >
                保存修改
              </Button>
              <Button onClick={handleCancel}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default UserEditPage;

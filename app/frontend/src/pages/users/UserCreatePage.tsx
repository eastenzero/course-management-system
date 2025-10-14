import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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

interface UserFormData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'admin' | 'teacher' | 'student';
  employee_id?: string;
  student_id?: string;
  is_active: boolean;
  phone?: string;
  department?: string;
  password: string;
  confirmPassword: string;
}

const UserCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

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
      setLoading(true);

      // 验证密码确认
      if (values.password !== values.confirmPassword) {
        message.error('两次输入的密码不一致');
        return;
      }

      // 移除确认密码字段
      const { confirmPassword, ...userData } = values;

      // 调用API创建用户
      await userAPI.createUser(userData);

      message.success('用户创建成功');
      navigate('/users/list');
    } catch (error) {
      console.error('创建用户失败:', error);
      message.error('创建失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/users/list');
  };

  const handleUserTypeChange = (userType: string) => {
    // 根据用户类型清空相关字段
    if (userType === 'student') {
      form.setFieldsValue({ employee_id: undefined });
    } else {
      form.setFieldsValue({ student_id: undefined });
    }
  };

  return (
    <div className="user-create-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleCancel}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>创建用户</Title>
        </Space>
        <p>填写用户基本信息和权限设置</p>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            is_active: true,
            user_type: 'student'
          }}
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
                    <Avatar size={80} icon={<UserOutlined />} />
                    <div style={{ marginTop: 8 }}>
                      <UploadOutlined /> 上传头像
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
                name="first_name"
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
                name="last_name"
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
                name="user_type"
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
                name="is_active"
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
                  prevValues.user_type !== currentValues.user_type
                }
              >
                {({ getFieldValue }) => {
                  const userType = getFieldValue('user_type');
                  if (userType === 'student') {
                    return (
                      <Form.Item
                        name="student_id"
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
                        name="employee_id"
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

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="password"
                label="密码"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6位' },
                  { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字' }
                ]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="confirmPassword"
                label="确认密码"
                dependencies={['password']}
                rules={[
                  { required: true, message: '请确认密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'));
                    },
                  }),
                ]}
              >
                <Input.Password placeholder="请再次输入密码" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                创建用户
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

export default UserCreatePage;

import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Form,
  Input,
  Button,
  Row,
  Col,
  message,
  Space,
  Upload,
  Avatar,
  Divider,
  Tag,
  Descriptions,
} from 'antd';
import {
  UserOutlined,
  UploadOutlined,
  SaveOutlined,
  EditOutlined,
  MailOutlined,
  PhoneOutlined,
  IdcardOutlined,
} from '@ant-design/icons';
import { UserAvatar } from '../../components/business';
import { authAPI } from '../../api/auth'; // 使用authAPI而不是userAPI

const { Title } = Typography;

interface UserInfo {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  userType: 'admin' | 'teacher' | 'student';
  employeeId?: string;
  studentId?: string;
  avatar?: string;
  phone?: string;
  department?: string;
  createdAt: string;
  lastLoginAt?: string;
}

const PersonalInfoPage: React.FC = () => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    // 模拟获取当前用户信息
    const fetchUserInfo = async () => {
      try {
        setLoading(true);
        
        // 禁用模拟数据，使用真实API
        const response = await authAPI.getCurrentUser(); // 使用authAPI而不是userAPI
        if (response.data.code === 200) {
          const userData = response.data.data;
          const userInfo: UserInfo = {
            id: userData.id.toString(),
            username: userData.username,
            email: userData.email,
            firstName: userData.first_name,
            lastName: userData.last_name,
            userType: userData.user_type,
            employeeId: userData.employee_id || '',
            phone: userData.phone || '',
            department: userData.department || '',
            createdAt: userData.created_at || '',
            lastLoginAt: '',
          };
          setUserInfo(userInfo);
          form.setFieldsValue(userInfo);
        } else {
          throw new Error(response.data.message || '获取用户信息失败');
        }
      } catch (error) {
        message.error('获取用户信息失败');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [form]);

  const handleEdit = () => {
    setEditing(true);
  };

  const handleCancel = () => {
    setEditing(false);
    if (userInfo) {
      form.setFieldsValue(userInfo);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      setSubmitting(true);
      
      // 调用API更新用户信息
      await authAPI.updateProfile(values); // 使用authAPI的updateProfile方法
      
      setUserInfo({ ...userInfo!, ...values });
      setEditing(false);
      message.success('个人信息更新成功');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '更新失败，请重试';
      message.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const getUserTypeText = (userType: string): string => {
    const typeMap = {
      admin: '管理员',
      teacher: '教师',
      student: '学生',
    };
    return typeMap[userType as keyof typeof typeMap] || userType;
  };

  const getUserTypeColor = (userType: string): string => {
    const colorMap = {
      admin: 'red',
      teacher: 'blue',
      student: 'green',
    };
    return colorMap[userType as keyof typeof colorMap] || 'default';
  };

  if (loading || !userInfo) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>加载中...</div>
      </div>
    );
  }

  return (
    <div className="personal-info-page">
      <div className="page-header">
        <Title level={2}>个人信息</Title>
        <p>查看和编辑个人基本信息</p>
      </div>

      <Row gutter={[24, 24]}>
        {/* 左侧：头像和基本信息 */}
        <Col xs={24} lg={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <UserAvatar
                user={userInfo}
                size={80}
                showName={false}
                showRole={false}
              />
              
              <div style={{ marginTop: '16px' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {userInfo.lastName}{userInfo.firstName}
                </Title>
                <div style={{ marginTop: '8px' }}>
                  <Tag color={getUserTypeColor(userInfo.userType)}>
                    {getUserTypeText(userInfo.userType)}
                  </Tag>
                </div>
              </div>

              {editing && (
                <div style={{ marginTop: '16px' }}>
                  <Upload
                    name="avatar"
                    showUploadList={false}
                    beforeUpload={() => false}
                  >
                    <Button icon={<UploadOutlined />} size="small">
                      更换头像
                    </Button>
                  </Upload>
                </div>
              )}
            </div>

            <Divider />

            <Descriptions column={1} size="small">
              <Descriptions.Item 
                label={<Space><IdcardOutlined />工号/学号</Space>}
              >
                {userInfo.employeeId || userInfo.studentId}
              </Descriptions.Item>
              <Descriptions.Item 
                label={<Space><MailOutlined />邮箱</Space>}
              >
                {userInfo.email}
              </Descriptions.Item>
              <Descriptions.Item 
                label={<Space><PhoneOutlined />手机</Space>}
              >
                {userInfo.phone || '未设置'}
              </Descriptions.Item>
              <Descriptions.Item label="院系/部门">
                {userInfo.department}
              </Descriptions.Item>
              <Descriptions.Item label="注册时间">
                {userInfo.createdAt}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录">
                {userInfo.lastLoginAt || '从未登录'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 右侧：编辑表单 */}
        <Col xs={24} lg={16}>
          <Card
            title="基本信息"
            extra={
              !editing ? (
                <Button 
                  type="primary" 
                  icon={<EditOutlined />}
                  onClick={handleEdit}
                >
                  编辑信息
                </Button>
              ) : null
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              disabled={!editing}
            >
              <Row gutter={16}>
                <Col span={12}>
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
                <Col span={12}>
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

              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, max: 20, message: '用户名长度为3-20个字符' }
                ]}
              >
                <Input placeholder="如：zhang.prof" disabled />
              </Form.Item>

              <Form.Item
                name="department"
                label="院系/部门"
              >
                <Input placeholder="院系或部门" disabled />
              </Form.Item>

              {editing && (
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
              )}
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PersonalInfoPage;

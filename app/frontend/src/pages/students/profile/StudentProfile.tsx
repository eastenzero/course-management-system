import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  DatePicker,
  Upload,
  Avatar,
  message,
  Descriptions,
  Row,
  Col,
  Progress,
  Statistic,
  Typography,
  Divider,
  Space,
  Spin
} from 'antd';
import {
  UserOutlined,
  EditOutlined,
  SaveOutlined,
  UploadOutlined,
  TrophyOutlined,
  BookOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { studentAPI } from '../../../services/studentAPI';
import type { StudentProfile as StudentProfileType } from '../../../services/studentAPI';

const { Option } = Select;
const { Title, Text } = Typography;

const StudentProfile: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [profile, setProfile] = useState<StudentProfileType | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await studentAPI.getProfile();
      setProfile(response.data);
      form.setFieldsValue(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取个人信息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      setSaving(true);
      const response = await studentAPI.updateProfile(values);
      setProfile(response.data);
      setEditing(false);
      message.success('个人信息更新成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '更新个人信息失败');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    form.setFieldsValue(profile);
    setEditing(false);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>个人信息</Title>

      <Row gutter={[24, 24]}>
        {/* 基本信息卡片 */}
        <Col xs={24} lg={16}>
          <Card
            title="基本信息"
            extra={
              <Space>
                {!editing ? (
                  <Button
                    type="primary"
                    icon={<EditOutlined />}
                    onClick={() => setEditing(true)}
                  >
                    编辑
                  </Button>
                ) : (
                  <>
                    <Button onClick={handleCancel}>
                      取消
                    </Button>
                    <Button
                      type="primary"
                      icon={<SaveOutlined />}
                      loading={saving}
                      onClick={() => form.submit()}
                    >
                      保存
                    </Button>
                  </>
                )}
              </Space>
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              disabled={!editing}
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="姓名"
                    name={['user_info', 'first_name']}
                    rules={[{ required: true, message: '请输入姓名' }]}
                  >
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="学号"
                    name={['user_info', 'student_id']}
                  >
                    <Input disabled />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="邮箱"
                    name={['user_info', 'email']}
                    rules={[
                      { required: true, message: '请输入邮箱' },
                      { type: 'email', message: '请输入有效的邮箱地址' }
                    ]}
                  >
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="院系"
                    name={['user_info', 'department']}
                  >
                    <Input disabled />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="专业"
                    name="major"
                    rules={[{ required: true, message: '请输入专业' }]}
                  >
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="班级"
                    name="class_name"
                    rules={[{ required: true, message: '请输入班级' }]}
                  >
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="入学年份"
                    name="admission_year"
                    rules={[{ required: true, message: '请选择入学年份' }]}
                  >
                    <Select>
                      {Array.from({ length: 10 }, (_, i) => {
                        const year = new Date().getFullYear() - i;
                        return (
                          <Option key={year} value={year}>
                            {year}年
                          </Option>
                        );
                      })}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="学籍状态"
                    name="enrollment_status"
                  >
                    <Select disabled>
                      <Option value="enrolled">在读</Option>
                      <Option value="suspended">休学</Option>
                      <Option value="graduated">毕业</Option>
                      <Option value="dropped">退学</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="紧急联系人"
                    name="emergency_contact"
                  >
                    <Input />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="紧急联系电话"
                    name="emergency_phone"
                  >
                    <Input />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>

        {/* 学业统计卡片 */}
        <Col xs={24} lg={8}>
          <Card title="学业统计" style={{ marginBottom: '24px' }}>
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Statistic
                  title="GPA"
                  value={profile.gpa}
                  precision={2}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ 
                    color: profile.gpa >= 3.5 ? '#52c41a' : profile.gpa >= 3.0 ? '#1890ff' : '#faad14' 
                  }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总学分"
                  value={profile.total_credits}
                  prefix={<BookOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="已完成"
                  value={profile.completed_credits}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={24}>
                <div style={{ marginTop: '16px' }}>
                  <Text>学分完成度</Text>
                  <Progress
                    percent={profile.completion_rate}
                    status={profile.completion_rate >= 80 ? 'success' : 'active'}
                    format={(percent) => `${percent}%`}
                  />
                </div>
              </Col>
            </Row>
          </Card>

          {/* 头像上传卡片 */}
          <Card title="头像">
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={120}
                icon={<UserOutlined />}
                style={{ marginBottom: '16px' }}
              />
              <div>
                <Upload
                  showUploadList={false}
                  beforeUpload={() => {
                    message.info('头像上传功能开发中...');
                    return false;
                  }}
                >
                  <Button icon={<UploadOutlined />}>
                    更换头像
                  </Button>
                </Upload>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 详细信息展示 */}
      <Card title="详细信息" style={{ marginTop: '24px' }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="用户名">
            {profile.user_info.username}
          </Descriptions.Item>
          <Descriptions.Item label="学号">
            {profile.user_info.student_id}
          </Descriptions.Item>
          <Descriptions.Item label="姓名">
            {profile.user_info.first_name} {profile.user_info.last_name}
          </Descriptions.Item>
          <Descriptions.Item label="邮箱">
            {profile.user_info.email}
          </Descriptions.Item>
          <Descriptions.Item label="院系">
            {profile.user_info.department}
          </Descriptions.Item>
          <Descriptions.Item label="专业">
            {profile.major}
          </Descriptions.Item>
          <Descriptions.Item label="班级">
            {profile.class_name}
          </Descriptions.Item>
          <Descriptions.Item label="入学年份">
            {profile.admission_year}年
          </Descriptions.Item>
          <Descriptions.Item label="学籍状态">
            {profile.enrollment_status_display}
          </Descriptions.Item>
          <Descriptions.Item label="GPA">
            {profile.gpa}
          </Descriptions.Item>
          <Descriptions.Item label="总学分">
            {profile.total_credits}
          </Descriptions.Item>
          <Descriptions.Item label="已完成学分">
            {profile.completed_credits}
          </Descriptions.Item>
          <Descriptions.Item label="剩余学分">
            {profile.remaining_credits}
          </Descriptions.Item>
          <Descriptions.Item label="完成率">
            {profile.completion_rate}%
          </Descriptions.Item>
          <Descriptions.Item label="紧急联系人">
            {profile.emergency_contact || '未设置'}
          </Descriptions.Item>
          <Descriptions.Item label="紧急联系电话">
            {profile.emergency_phone || '未设置'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default StudentProfile;

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  Upload,
  Avatar,
  Row,
  Col,
  Typography,
  Divider,
  message,
  Spin,
  Space,
  Tag,
} from 'antd';
import {
  UserOutlined,
  EditOutlined,
  SaveOutlined,
  CameraOutlined,
  PhoneOutlined,
  MailOutlined,
  HomeOutlined,
  BookOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useAppSelector } from '../../../store';
import { teacherAPI } from '../../../services/teacherAPI';
import { GlassCard } from '../../../components/glass/GlassCard';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface TeacherProfileData {
  id?: number;
  user_info: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  title: string;
  title_display: string;
  research_area: string;
  office_location: string;
  office_hours: string;
  teaching_experience: string;
  education_background: string;
  office_phone: string;
  personal_website: string;
  teaching_courses_count: number;
  is_active_teacher: boolean;
}

const TeacherProfile: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [profileData, setProfileData] = useState<TeacherProfileData | null>(null);
  const [uploading, setUploading] = useState(false);
  
  const { user } = useAppSelector(state => state.auth);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getProfile();
      setProfileData(response.data);
      form.setFieldsValue({
        first_name: response.data.user_info.first_name,
        last_name: response.data.user_info.last_name,
        email: response.data.user_info.email,
        title: response.data.title,
        research_area: response.data.research_area,
        office_location: response.data.office_location,
        office_hours: response.data.office_hours,
        teaching_experience: response.data.teaching_experience,
        education_background: response.data.education_background,
        office_phone: response.data.office_phone,
        personal_website: response.data.personal_website,
      });
    } catch (error) {
      console.error('获取个人信息失败:', error);
      // 使用模拟数据
      const mockProfile: TeacherProfileData = {
        id: 1,
        user_info: {
          id: 1,
          username: 'teacher001',
          email: 'teacher@example.com',
          first_name: '张',
          last_name: '教授',
          avatar: undefined
        },
        title: 'professor',
        title_display: '教授',
        research_area: '计算机科学',
        office_location: '科研楼 A301',
        office_hours: '周一至周五 14:00-16:00',
        teaching_experience: '15年',
        education_background: '计算机科学博士',
        office_phone: '010-12345678',
        personal_website: 'https://example.com/teacher',
        teaching_courses_count: 8,
        is_active_teacher: true
      };
      setProfileData(mockProfile);
      form.setFieldsValue({
        first_name: mockProfile.user_info.first_name,
        last_name: mockProfile.user_info.last_name,
        email: mockProfile.user_info.email,
        title: mockProfile.title,
        research_area: mockProfile.research_area,
        office_location: mockProfile.office_location,
        office_hours: mockProfile.office_hours,
        teaching_experience: mockProfile.teaching_experience,
        education_background: mockProfile.education_background,
        office_phone: mockProfile.office_phone,
        personal_website: mockProfile.personal_website,
      });
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      setLoading(true);
      await teacherAPI.updateProfile(values);
      message.success('个人信息更新成功');
      setEditing(false);
      fetchProfile();
    } catch (error) {
      message.error('更新个人信息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (file: File) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('avatar', file);
      await teacherAPI.uploadAvatar(formData);
      message.success('头像上传成功');
      fetchProfile();
    } catch (error) {
      message.error('头像上传失败');
    } finally {
      setUploading(false);
    }
  };

  const titleOptions = [
    { value: 'assistant', label: '助教' },
    { value: 'lecturer', label: '讲师' },
    { value: 'associate_professor', label: '副教授' },
    { value: 'professor', label: '教授' },
    { value: 'researcher', label: '研究员' },
  ];

  if (loading && !profileData) {
    return (
      <div className="glass-page-background">
        <DynamicBackground
          density={0.08}
          speed={0.8}
          lineMaxDist={120}
          triMaxDist={80}
        />
        <div className="glass-content" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
          <Spin size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className="glass-page-background">
      <DynamicBackground
        density={0.08}
        speed={0.8}
        lineMaxDist={120}
        triMaxDist={80}
      />
      
      <div className="glass-content" style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2}>个人档案</Title>
      
      <Row gutter={[24, 24]}>
        {/* 基本信息卡片 */}
        <Col xs={24} lg={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{ position: 'relative', display: 'inline-block' }}>
                <Avatar
                  size={120}
                  src={profileData?.user_info.avatar}
                  icon={<UserOutlined />}
                />
                {editing && (
                  <Upload
                    showUploadList={false}
                    beforeUpload={(file) => {
                      handleAvatarUpload(file);
                      return false;
                    }}
                    accept="image/*"
                  >
                    <Button
                      type="primary"
                      shape="circle"
                      icon={<CameraOutlined />}
                      size="small"
                      loading={uploading}
                      style={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                      }}
                    />
                  </Upload>
                )}
              </div>
              
              <div style={{ marginTop: '16px' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {profileData?.user_info.first_name} {profileData?.user_info.last_name}
                </Title>
                <Text type="secondary">{profileData?.user_info.username}</Text>
                <br />
                <Tag color="blue" style={{ marginTop: '8px' }}>
                  {profileData?.title_display}
                </Tag>
              </div>
            </div>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <MailOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                <Text>{profileData?.user_info.email}</Text>
              </div>
              
              {profileData?.office_phone && (
                <div>
                  <PhoneOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  <Text>{profileData.office_phone}</Text>
                </div>
              )}
              
              {profileData?.office_location && (
                <div>
                  <HomeOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  <Text>{profileData.office_location}</Text>
                </div>
              )}
              
              {profileData?.office_hours && (
                <div>
                  <ClockCircleOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  <Text>{profileData.office_hours}</Text>
                </div>
              )}
              
              <div>
                <BookOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                <Text>授课课程: {profileData?.teaching_courses_count || 0} 门</Text>
              </div>
            </Space>
          </Card>
        </Col>

        {/* 详细信息表单 */}
        <Col xs={24} lg={16}>
          <Card
            title="详细信息"
            extra={
              <Space>
                {editing ? (
                  <>
                    <Button onClick={() => setEditing(false)}>取消</Button>
                    <Button
                      type="primary"
                      icon={<SaveOutlined />}
                      onClick={() => form.submit()}
                      loading={loading}
                    >
                      保存
                    </Button>
                  </>
                ) : (
                  <Button
                    type="primary"
                    icon={<EditOutlined />}
                    onClick={() => setEditing(true)}
                  >
                    编辑
                  </Button>
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
              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="姓"
                    name="last_name"
                    rules={[{ required: true, message: '请输入姓' }]}
                  >
                    <Input placeholder="请输入姓" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="名"
                    name="first_name"
                    rules={[{ required: true, message: '请输入名' }]}
                  >
                    <Input placeholder="请输入名" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="邮箱"
                    name="email"
                    rules={[
                      { required: true, message: '请输入邮箱' },
                      { type: 'email', message: '请输入有效的邮箱地址' }
                    ]}
                  >
                    <Input placeholder="请输入邮箱" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    label="职称"
                    name="title"
                    rules={[{ required: true, message: '请选择职称' }]}
                  >
                    <Select placeholder="请选择职称">
                      {titleOptions.map(option => (
                        <Option key={option.value} value={option.value}>
                          {option.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item label="办公室位置" name="office_location">
                    <Input placeholder="如：理学院A座301室" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item label="办公电话" name="office_phone">
                    <Input placeholder="请输入办公电话" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="个人网站" name="personal_website">
                <Input placeholder="请输入个人网站地址" />
              </Form.Item>

              <Form.Item label="答疑时间" name="office_hours">
                <TextArea
                  rows={3}
                  placeholder="请填写您的答疑时间安排"
                />
              </Form.Item>

              <Form.Item label="研究方向" name="research_area">
                <TextArea
                  rows={4}
                  placeholder="请简要描述您的研究领域和方向"
                />
              </Form.Item>

              <Form.Item label="教学经历" name="teaching_experience">
                <TextArea
                  rows={4}
                  placeholder="请描述您的教学经历"
                />
              </Form.Item>

              <Form.Item label="教育背景" name="education_background">
                <TextArea
                  rows={4}
                  placeholder="请描述您的教育背景"
                />
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
      </div>
    </div>
  );
};

export default TeacherProfile;

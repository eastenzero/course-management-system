import React, { useState, useEffect } from 'react';
import {
  List,
  Button,
  Tag,
  Space,
  Modal,
  message,
  Descriptions,
  Progress,
  Typography,
  Row,
  Col,
  Statistic,
  Avatar,
  Tooltip,
  Empty,
  Spin,
  Card
} from 'antd';
import {
  BookOutlined,
  UserOutlined,
  CalendarOutlined,
  TrophyOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  StarOutlined,
  ClockCircleOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { studentAPI } from '../../../services/studentAPI';
import { GlassCard } from '../../../components/glass/GlassCard';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Text, Title } = Typography;
const { confirm } = Modal;

interface Enrollment {
  id: number;
  course_info: {
    id: number;
    code: string;
    name: string;
    credits: number;
    hours: number;
    course_type: string;
    department: string;
    semester: string;
    description: string;
    teachers_info: any[];
  };
  status: string;
  status_display: string;
  score: number | null;
  grade: string;
  grade_display: string;
  enrolled_at: string;
  is_active: boolean;
}

const MyCourses: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<Enrollment[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Enrollment | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [dropping, setDropping] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchMyCourses();
  }, []);

  const fetchMyCourses = async () => {
    try {
      setLoading(true);
      const response = await studentAPI.getMyCourses();
      // 处理分页数据结构
      const coursesData = Array.isArray(response.data) ? response.data : response.data?.results || [];
      setCourses(coursesData);
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取我的课程失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDropCourse = async (courseId: number) => {
    try {
      setDropping(true);
      await studentAPI.dropCourse(courseId);
      message.success('退课成功！');
      fetchMyCourses(); // 刷新课程列表
    } catch (error: any) {
      message.error(error.response?.data?.error || '退课失败');
    } finally {
      setDropping(false);
    }
  };

  const showDropConfirm = (enrollment: Enrollment) => {
    confirm({
      title: '确认退课',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>您确定要退选以下课程吗？</p>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="课程名称">{enrollment.course_info.name}</Descriptions.Item>
            <Descriptions.Item label="课程代码">{enrollment.course_info.code}</Descriptions.Item>
            <Descriptions.Item label="学分">{enrollment.course_info.credits}</Descriptions.Item>
          </Descriptions>
          <p style={{ color: '#ff4d4f', marginTop: '8px' }}>
            注意：退课后可能无法重新选择该课程，请谨慎操作。
          </p>
        </div>
      ),
      onOk: () => handleDropCourse(enrollment.course_info.id),
      okText: '确认退课',
      cancelText: '取消',
      okType: 'danger',
    });
  };

  const showCourseDetail = (enrollment: Enrollment) => {
    setSelectedCourse(enrollment);
    setDetailModalVisible(true);
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      'enrolled': 'blue',
      'completed': 'green',
      'dropped': 'red',
      'failed': 'red'
    };
    return colorMap[status] || 'default';
  };

  const getGradeColor = (score: number | null) => {
    if (score === null) return '#666';
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  // 统计数据
  const statistics = {
    total: courses.length,
    enrolled: courses.filter(c => c.status === 'enrolled').length,
    completed: courses.filter(c => c.status === 'completed').length,
    totalCredits: courses.reduce((sum, c) => sum + c.course_info.credits, 0),
    averageScore: courses.filter(c => c.score !== null).length > 0 
      ? courses.filter(c => c.score !== null).reduce((sum, c) => sum + (c.score || 0), 0) / courses.filter(c => c.score !== null).length
      : 0
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
      }}>
        <Card style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" tip="加载中..." />
        </Card>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '24px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* 页面标题 */}
        <Card style={{ marginBottom: '24px', borderRadius: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <BookOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
            <div>
              <h1 style={{ color: '#1f2937', margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
                我的课程
              </h1>
              <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>
                查看已选课程和学习进度
              </p>
            </div>
          </div>
        </Card>

        {/* 统计概览 */}
        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable style={{ borderRadius: '12px' }}>
              <Statistic
                title="总课程数"
                value={statistics.total}
                prefix={<BookOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable style={{ borderRadius: '12px' }}>
              <Statistic
                title="在读课程"
                value={statistics.enrolled}
                prefix={<CalendarOutlined style={{ color: '#52c41a' }} />}
                  valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable style={{ borderRadius: '12px' }}>
              <Statistic
                title="总学分"
                value={statistics.totalCredits}
                prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
                valueStyle={{ color: '#faad14', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable style={{ borderRadius: '12px' }}>
              <Statistic
                title="平均成绩"
                value={statistics.averageScore}
                precision={1}
                suffix="分"
                prefix={<StarOutlined style={{ color: '#722ed1' }} />}
                valueStyle={{ color: '#722ed1', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 课程列表 */}
        <Card style={{ borderRadius: '12px' }}>
          {courses.length === 0 ? (
            <Empty
              description="暂无选课记录"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button
                type="primary"
                onClick={() => navigate('/students/course-selection')}
              >
                去选课
              </Button>
            </Empty>
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {courses.map((enrollment, index) => (
                <div
                  key={enrollment.id}
                  style={{
                    background: '#ffffff',
                    borderRadius: '12px',
                    padding: '20px',
                    border: '1px solid #e2e8f0',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                    <Avatar
                      size={64}
                      style={{ backgroundColor: '#1890ff', flexShrink: 0 }}
                      icon={<BookOutlined />}
                    />

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <h3 style={{ color: '#1f2937', margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
                          {enrollment.course_info.name}
                        </h3>
                        <Tag color={getStatusColor(enrollment.status)}>
                          {enrollment.status_display}
                        </Tag>
                        <Tag color="blue">{enrollment.course_info.course_type}</Tag>
                      </div>

                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ color: '#6b7280', marginBottom: '4px' }}>
                          <BookOutlined style={{ marginRight: '8px' }} />
                          {enrollment.course_info.code} | {enrollment.course_info.credits}学分 | {enrollment.course_info.hours}学时
                        </div>
                        <div style={{ color: '#6b7280', marginBottom: '4px' }}>
                          <UserOutlined style={{ marginRight: '8px' }} />
                          授课教师：{enrollment.course_info.teachers_info.map(t => t.name).join(', ')}
                        </div>
                        <div style={{ color: '#6b7280', marginBottom: '4px' }}>
                          <CalendarOutlined style={{ marginRight: '8px' }} />
                          开课学期：{enrollment.course_info.semester}
                        </div>
                        {enrollment.score !== null && (
                          <div style={{ color: '#6b7280' }}>
                            <TrophyOutlined style={{ marginRight: '8px' }} />
                            成绩：
                            <span style={{
                              color: getGradeColor(enrollment.score),
                              fontWeight: 'bold',
                              marginLeft: '4px'
                            }}>
                              {enrollment.score}分 ({enrollment.grade})
                            </span>
                          </div>
                        )}
                      </div>

                      <div style={{
                        fontSize: '12px',
                        color: '#9ca3af',
                        marginBottom: '12px'
                      }}>
                        <ClockCircleOutlined style={{ marginRight: '4px' }} />
                        选课时间：{new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexShrink: 0 }}>
                      <Button
                        type="primary"
                        icon={<EyeOutlined />}
                        onClick={() => showCourseDetail(enrollment)}
                        size="small"
                      >
                        详情
                      </Button>
                      {enrollment.status === 'enrolled' && (
                        <Button
                          danger
                          icon={<DeleteOutlined />}
                          loading={dropping}
                          onClick={() => showDropConfirm(enrollment)}
                          size="small"
                        >
                          退课
                        </Button>
                      )}
                      {enrollment.status === 'completed' && (
                        <Button
                          type="default"
                          icon={<StarOutlined />}
                          onClick={() => navigate(`/students/courses/${enrollment.id}/evaluate`)}
                          style={{
                            color: '#faad14',
                            borderColor: '#faad14'
                          }}
                          size="small"
                        >
                          评价
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

      {/* 课程详情模态框 */}
      <Modal
        title={
          <span style={{ color: '#1890ff', fontSize: '18px', fontWeight: 'bold' }}>
            课程详情
          </span>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button
            key="cancel"
            onClick={() => setDetailModalVisible(false)}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: 'white'
            }}
          >
            关闭
          </Button>,
          selectedCourse?.status === 'enrolled' && (
            <Button
              key="drop"
              danger
              loading={dropping}
              onClick={() => {
                setDetailModalVisible(false);
                showDropConfirm(selectedCourse);
              }}
              style={{
                background: 'rgba(255, 77, 79, 0.8)',
                borderColor: 'rgba(255, 77, 79, 0.8)'
              }}
            >
              退课
            </Button>
          ),
        ]}
        width={800}
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)'
        }}
      >
        {selectedCourse && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="课程名称" span={2}>
              {selectedCourse.course_info.name}
            </Descriptions.Item>
            <Descriptions.Item label="课程代码">
              {selectedCourse.course_info.code}
            </Descriptions.Item>
            <Descriptions.Item label="学分">
              {selectedCourse.course_info.credits}
            </Descriptions.Item>
            <Descriptions.Item label="学时">
              {selectedCourse.course_info.hours}
            </Descriptions.Item>
            <Descriptions.Item label="课程类型">
              <Tag>{selectedCourse.course_info.course_type}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="开课院系">
              {selectedCourse.course_info.department}
            </Descriptions.Item>
            <Descriptions.Item label="开课学期">
              {selectedCourse.course_info.semester}
            </Descriptions.Item>
            <Descriptions.Item label="选课状态">
              <Tag color={getStatusColor(selectedCourse.status)}>
                {selectedCourse.status_display}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="授课教师" span={2}>
              {selectedCourse.course_info.teachers_info.map(teacher => teacher.name).join(', ')}
            </Descriptions.Item>
            {selectedCourse.score !== null && (
              <Descriptions.Item label="成绩" span={2}>
                <Text strong style={{ color: getGradeColor(selectedCourse.score) }}>
                  {selectedCourse.score}分 ({selectedCourse.grade})
                </Text>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="选课时间" span={2}>
              {new Date(selectedCourse.enrolled_at).toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="课程描述" span={2}>
              {selectedCourse.course_info.description || '暂无描述'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
      </div>
    </div>
  );
};

export default MyCourses;

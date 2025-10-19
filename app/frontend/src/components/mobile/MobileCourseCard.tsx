import React from 'react';
import { Card, Tag, Space, Typography, Progress, Button } from 'antd';
import {
  ClockCircleOutlined,
  UserOutlined,
  EnvironmentOutlined,
  BookOutlined,
  StarOutlined
} from '@ant-design/icons';
import '../../styles/mobile.css';

const { Text, Title } = Typography;

interface MobileCourseCardProps {
  course: {
    id: number;
    name: string;
    code: string;
    credits: number;
    semester: string;
    department: string;
    teachers: Array<{
      id: number;
      name: string;
    }>;
    current_enrollment?: number;
    max_enrollment?: number;
    schedule?: Array<{
      day_of_week: number;
      start_time: string;
      end_time: string;
      classroom?: {
        name: string;
        building: string;
      };
    }>;
    grade?: string;
    score?: number;
    status?: 'enrolled' | 'available' | 'full' | 'completed';
  };
  mode?: 'browse' | 'enrolled' | 'teaching';
  onAction?: (action: string, courseId: number) => void;
  showProgress?: boolean;
  className?: string;
}

const MobileCourseCard: React.FC<MobileCourseCardProps> = ({
  course,
  mode = 'browse',
  onAction,
  showProgress = false,
  className = ''
}) => {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'enrolled':
        return 'blue';
      case 'available':
        return 'green';
      case 'full':
        return 'red';
      case 'completed':
        return 'purple';
      default:
        return 'default';
    }
  };

  const getStatusText = (status?: string) => {
    switch (status) {
      case 'enrolled':
        return '已选课';
      case 'available':
        return '可选';
      case 'full':
        return '已满';
      case 'completed':
        return '已完成';
      default:
        return '未知';
    }
  };

  const formatSchedule = (schedule?: Array<any>) => {
    if (!schedule || schedule.length === 0) return '时间待定';
    
    const dayNames = ['日', '一', '二', '三', '四', '五', '六'];
    return schedule.map(item => 
      `周${dayNames[item.day_of_week]} ${item.start_time}-${item.end_time}`
    ).join(', ');
  };

  const getEnrollmentProgress = () => {
    if (!course.current_enrollment || !course.max_enrollment) return 0;
    return (course.current_enrollment / course.max_enrollment) * 100;
  };

  const renderActionButton = () => {
    switch (mode) {
      case 'browse':
        if (course.status === 'available') {
          return (
            <Button 
              type="primary" 
              size="small"
              onClick={() => onAction?.('enroll', course.id)}
            >
              选课
            </Button>
          );
        } else if (course.status === 'enrolled') {
          return (
            <Button 
              danger 
              size="small"
              onClick={() => onAction?.('drop', course.id)}
            >
              退课
            </Button>
          );
        }
        break;
      case 'enrolled':
        return (
          <Space>
            <Button 
              size="small"
              onClick={() => onAction?.('view_grades', course.id)}
            >
              查看成绩
            </Button>
            <Button 
              size="small"
              onClick={() => onAction?.('view_schedule', course.id)}
            >
              课程表
            </Button>
          </Space>
        );
      case 'teaching':
        return (
          <Space>
            <Button 
              type="primary" 
              size="small"
              onClick={() => onAction?.('manage_students', course.id)}
            >
              学生管理
            </Button>
            <Button 
              size="small"
              onClick={() => onAction?.('grade_entry', course.id)}
            >
              成绩录入
            </Button>
          </Space>
        );
    }
    return null;
  };

  return (
    <Card 
      className={`mobile-course-card ${className}`}
      size="small"
      hoverable
    >
      <div className="course-info">
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <Title level={5} style={{ margin: 0, marginRight: 8 }}>
              {course.name}
            </Title>
            {course.status && (
              <Tag color={getStatusColor(course.status)} size="small">
                {getStatusText(course.status)}
              </Tag>
            )}
          </div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {course.code} | {course.credits}学分 | {course.department}
          </Text>
        </div>
        {course.score !== undefined && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 18, fontWeight: 600, color: '#52c41a' }}>
              {course.score}
            </div>
            {course.grade && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {course.grade}
              </Text>
            )}
          </div>
        )}
      </div>

      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        {/* 教师信息 */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <UserOutlined style={{ marginRight: 4, color: '#666' }} />
          <Text style={{ fontSize: 12 }}>
            {course.teachers.map(t => t.name).join(', ')}
          </Text>
        </div>

        {/* 时间安排 */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <ClockCircleOutlined style={{ marginRight: 4, color: '#666' }} />
          <Text style={{ fontSize: 12 }}>
            {formatSchedule(course.schedule)}
          </Text>
        </div>

        {/* 教室信息 */}
        {course.schedule && course.schedule[0]?.classroom && (
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <EnvironmentOutlined style={{ marginRight: 4, color: '#666' }} />
            <Text style={{ fontSize: 12 }}>
              {course.schedule[0].classroom.building} {course.schedule[0].classroom.name}
            </Text>
          </div>
        )}

        {/* 选课进度 */}
        {showProgress && course.current_enrollment !== undefined && course.max_enrollment !== undefined && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text style={{ fontSize: 12 }}>选课人数</Text>
              <Text style={{ fontSize: 12 }}>
                {course.current_enrollment}/{course.max_enrollment}
              </Text>
            </div>
            <Progress 
              percent={getEnrollmentProgress()} 
              size="small"
              strokeColor={getEnrollmentProgress() > 90 ? '#ff4d4f' : '#1890ff'}
            />
          </div>
        )}

        {/* 操作按钮 */}
        {renderActionButton() && (
          <div style={{ marginTop: 8, textAlign: 'right' }}>
            {renderActionButton()}
          </div>
        )}
      </Space>
    </Card>
  );
};

export default MobileCourseCard;

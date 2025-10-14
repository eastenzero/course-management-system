import React from 'react';
import { Card, Tag, Avatar, Space, Typography, Progress, Button, Tooltip } from 'antd';
import {
  BookOutlined,
  UserOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  TrophyOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

export interface CourseCardProps {
  course: {
    id: number;
    code: string;
    name: string;
    credits: number;
    hours: number;
    course_type: string;
    department: string;
    semester: string;
    description?: string;
    teachers?: Array<{
      id: number;
      name: string;
      title?: string;
    }>;
    enrollment?: {
      current: number;
      max: number;
      is_full?: boolean;
    };
    grade?: {
      score?: number;
      letter?: string;
    };
    status?: string;
    is_published?: boolean;
  };
  mode?: 'student' | 'teacher' | 'admin';
  actions?: React.ReactNode[];
  onClick?: () => void;
  showProgress?: boolean;
  showGrade?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
  mode = 'student',
  actions,
  onClick,
  showProgress = false,
  showGrade = false,
  className,
  style
}) => {
  const getCourseTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'required': 'red',
      'elective': 'blue',
      'public': 'green',
      'professional': 'orange'
    };
    return colorMap[type] || 'default';
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

  const getGradeColor = (score?: number) => {
    if (!score) return '#666';
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const renderEnrollmentProgress = () => {
    if (!course.enrollment || !showProgress) return null;
    
    const { current, max, is_full } = course.enrollment;
    const percentage = (current / max) * 100;
    
    return (
      <div style={{ marginTop: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <Text style={{ fontSize: '12px' }}>选课情况</Text>
          <Text style={{ fontSize: '12px' }}>{current}/{max}</Text>
        </div>
        <Progress
          percent={percentage}
          size="small"
          status={is_full ? 'exception' : 'active'}
          format={() => ''}
        />
      </div>
    );
  };

  const renderGrade = () => {
    if (!course.grade || !showGrade) return null;
    
    const { score, letter } = course.grade;
    
    return (
      <div style={{ textAlign: 'center', marginTop: '8px' }}>
        {score !== undefined ? (
          <>
            <div style={{ 
              fontSize: '18px', 
              fontWeight: 'bold', 
              color: getGradeColor(score),
              marginBottom: '4px'
            }}>
              {score}分
            </div>
            {letter && (
              <Tag color={getGradeColor(score)}>
                {letter}
              </Tag>
            )}
          </>
        ) : (
          <Text type="secondary">未录入</Text>
        )}
      </div>
    );
  };

  return (
    <Card
      className={className}
      style={{ 
        cursor: onClick ? 'pointer' : 'default',
        ...style 
      }}
      onClick={onClick}
      actions={actions}
      hoverable={!!onClick}
    >
      <div style={{ marginBottom: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <Title level={5} style={{ margin: 0, marginBottom: '4px' }}>
              {course.name}
            </Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {course.code}
            </Text>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
            <Tag color={getCourseTypeColor(course.course_type)}>
              {course.course_type}
            </Tag>
            {course.status && (
              <Tag color={getStatusColor(course.status)}>
                {course.status}
              </Tag>
            )}
            {course.is_published !== undefined && (
              <Tag color={course.is_published ? 'green' : 'orange'}>
                {course.is_published ? '已发布' : '未发布'}
              </Tag>
            )}
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '12px' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrophyOutlined style={{ color: '#faad14' }} />
            <Text style={{ fontSize: '12px' }}>
              {course.credits}学分 | {course.hours}学时
            </Text>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CalendarOutlined style={{ color: '#1890ff' }} />
            <Text style={{ fontSize: '12px' }}>
              {course.semester} | {course.department}
            </Text>
          </div>

          {course.teachers && course.teachers.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <UserOutlined style={{ color: '#52c41a' }} />
              <Text style={{ fontSize: '12px' }}>
                {course.teachers.map(t => t.name).join(', ')}
              </Text>
            </div>
          )}
        </Space>
      </div>

      {course.description && (
        <div style={{ marginBottom: '12px' }}>
          <Tooltip title={course.description}>
            <Text 
              type="secondary" 
              style={{ 
                fontSize: '12px',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {course.description}
            </Text>
          </Tooltip>
        </div>
      )}

      {renderEnrollmentProgress()}
      {renderGrade()}
    </Card>
  );
};

export default CourseCard;

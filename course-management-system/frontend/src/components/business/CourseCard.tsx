import React from 'react';
import { Card, Tag, Progress, Space, Avatar, Tooltip } from 'antd';
import {
  BookOutlined,
  UserOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  EyeOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

interface Course {
  id: string;
  name: string;
  code: string;
  credits: number;
  department: string;
  teacher: string;
  capacity: number;
  enrolled: number;
  status: 'active' | 'inactive';
  description?: string;
  semester?: string;
}

interface CourseCardProps {
  course: Course;
  showActions?: boolean;
  size?: 'default' | 'small';
  onClick?: (course: Course) => void;
  onEdit?: (course: Course) => void;
  onView?: (course: Course) => void;
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
  showActions = true,
  size = 'default',
  onClick,
  onEdit,
  onView,
}) => {
  const navigate = useNavigate();

  const enrollmentRate = (course.enrolled / course.capacity) * 100;

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'success' : 'default';
  };

  const getStatusText = (status: string) => {
    return status === 'active' ? '开放选课' : '暂停选课';
  };

  const getEnrollmentColor = (rate: number) => {
    if (rate >= 90) return '#ff4d4f';
    if (rate >= 70) return '#faad14';
    return '#52c41a';
  };

  const handleCardClick = () => {
    if (onClick) {
      onClick(course);
    } else {
      navigate(`/courses/${course.id}`);
    }
  };

  const handleView = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onView) {
      onView(course);
    } else {
      navigate(`/courses/${course.id}`);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(course);
    } else {
      navigate(`/courses/${course.id}/edit`);
    }
  };

  const cardStyle = {
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    height: size === 'small' ? 'auto' : '280px',
  };

  const cardBodyStyle = {
    padding: size === 'small' ? '12px' : '16px',
    height: '100%',
    display: 'flex',
    flexDirection: 'column' as const,
  };

  return (
    <Card
      hoverable
      style={cardStyle}
      bodyStyle={cardBodyStyle}
      onClick={handleCardClick}
      actions={
        showActions
          ? [
              <Tooltip title="查看详情" key="view">
                <EyeOutlined onClick={handleView} />
              </Tooltip>,
              <Tooltip title="编辑课程" key="edit">
                <EditOutlined onClick={handleEdit} />
              </Tooltip>,
            ]
          : undefined
      }
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* 课程头部信息 */}
        <div style={{ marginBottom: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <h4 style={{ 
                margin: 0, 
                fontSize: size === 'small' ? '14px' : '16px',
                fontWeight: 'bold',
                color: '#1890ff',
                marginBottom: '4px'
              }}>
                {course.name}
              </h4>
              <div style={{ 
                color: '#666', 
                fontSize: size === 'small' ? '12px' : '13px',
                marginBottom: '8px'
              }}>
                <Space size="small">
                  <BookOutlined />
                  <span>{course.code}</span>
                  <span>•</span>
                  <span>{course.credits}学分</span>
                </Space>
              </div>
            </div>
            <Tag color={getStatusColor(course.status)} style={{ marginLeft: '8px' }}>
              {getStatusText(course.status)}
            </Tag>
          </div>
        </div>

        {/* 教师和院系信息 */}
        <div style={{ marginBottom: '12px' }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Avatar size="small" icon={<UserOutlined />} style={{ marginRight: '8px' }} />
              <span style={{ fontSize: size === 'small' ? '12px' : '13px', color: '#666' }}>
                {course.teacher}
              </span>
            </div>
            <div style={{ 
              fontSize: size === 'small' ? '12px' : '13px', 
              color: '#666',
              marginLeft: '32px'
            }}>
              {course.department}
            </div>
          </Space>
        </div>

        {/* 选课情况 */}
        <div style={{ marginBottom: size === 'small' ? '8px' : '12px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '8px'
          }}>
            <Space size="small">
              <TeamOutlined style={{ color: '#666' }} />
              <span style={{ fontSize: size === 'small' ? '12px' : '13px', color: '#666' }}>
                选课情况
              </span>
            </Space>
            <span style={{ 
              fontSize: size === 'small' ? '12px' : '13px',
              fontWeight: 'bold'
            }}>
              {course.enrolled}/{course.capacity}
            </span>
          </div>
          <Progress
            percent={enrollmentRate}
            strokeColor={getEnrollmentColor(enrollmentRate)}
            size="small"
            showInfo={false}
          />
          <div style={{ 
            textAlign: 'center', 
            fontSize: '12px', 
            color: '#666',
            marginTop: '4px'
          }}>
            {enrollmentRate.toFixed(1)}% 已选课
          </div>
        </div>

        {/* 课程描述 */}
        {course.description && size !== 'small' && (
          <div style={{ 
            flex: 1,
            fontSize: '12px',
            color: '#666',
            lineHeight: '1.4',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}>
            {course.description}
          </div>
        )}

        {/* 学期信息 */}
        {course.semester && (
          <div style={{ 
            marginTop: 'auto',
            paddingTop: '8px',
            borderTop: '1px solid #f0f0f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <Space size="small">
              <ClockCircleOutlined style={{ color: '#666' }} />
              <span style={{ fontSize: '12px', color: '#666' }}>
                {course.semester}
              </span>
            </Space>
            {enrollmentRate >= 90 && (
              <Tag color="red">
                名额紧张
              </Tag>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

export default CourseCard;

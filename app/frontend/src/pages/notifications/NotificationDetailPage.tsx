import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Space,
  Tag,
  Descriptions,
  message,
  Spin,
  Alert,
  Divider,
} from 'antd';
import {
  ArrowLeftOutlined,
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  UserOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { notificationAPI } from '../../services/api';

const { Title, Paragraph } = Typography;

interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  sender_name?: string;
  sender_full_name?: string;
  time_since_created: string;
  extra_data?: any;
}

const NotificationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [notification, setNotification] = useState<Notification | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotificationDetail = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const response = await notificationAPI.getNotification(parseInt(id));
        setNotification(response.data);
      } catch (error) {
        console.error('获取通知详情失败:', error);
        message.error('获取通知详情失败');
      } finally {
        setLoading(false);
      }
    };

    fetchNotificationDetail();
  }, [id]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'course_enrollment':
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
      case 'grade_published':
        return <CheckOutlined style={{ color: '#52c41a' }} />;
      case 'assignment_due':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'schedule_change':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'system_announcement':
        return <BellOutlined style={{ color: '#722ed1' }} />;
      case 'course_reminder':
        return <ClockCircleOutlined style={{ color: '#13c2c2' }} />;
      case 'exam_notification':
        return <WarningOutlined style={{ color: '#fa541c' }} />;
      default:
        return <BellOutlined />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'course_enrollment':
        return 'blue';
      case 'grade_published':
        return 'green';
      case 'assignment_due':
        return 'orange';
      case 'schedule_change':
        return 'red';
      case 'system_announcement':
        return 'purple';
      case 'course_reminder':
        return 'cyan';
      case 'exam_notification':
        return 'volcano';
      default:
        return 'default';
    }
  };

  const getTypeText = (type: string) => {
    switch (type) {
      case 'course_enrollment':
        return '课程选课';
      case 'grade_published':
        return '成绩发布';
      case 'assignment_due':
        return '作业截止';
      case 'schedule_change':
        return '课程表变更';
      case 'system_announcement':
        return '系统公告';
      case 'course_reminder':
        return '课程提醒';
      case 'exam_notification':
        return '考试通知';
      default:
        return type;
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return '紧急';
      case 'high':
        return '高';
      case 'normal':
        return '普通';
      case 'low':
        return '低';
      default:
        return priority;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'red';
      case 'high':
        return 'orange';
      case 'normal':
        return 'blue';
      case 'low':
        return 'green';
      default:
        return 'default';
    }
  };

  const handleMarkAsRead = async () => {
    if (notification && !notification.is_read) {
      try {
        await notificationAPI.markAsRead([notification.id]);
        setNotification({ ...notification, is_read: true });
        message.success('已标记为已读');
      } catch (error) {
        console.error('标记已读失败:', error);
        message.error('标记已读失败');
      }
    }
  };

  const handleBack = () => {
    navigate('/notifications/list');
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

  if (!notification) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>通知不存在</Title>
        <Button onClick={handleBack}>
          返回通知列表
        </Button>
      </div>
    );
  }

  return (
    <div className="notification-detail-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleBack}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            <Space>
              {getTypeIcon(notification.notification_type)}
              <span>通知详情</span>
              {!notification.is_read && (
                <Tag color="red" size="small">未读</Tag>
              )}
            </Space>
          </Title>
        </Space>
        <Space>
          {!notification.is_read && (
            <Button onClick={handleMarkAsRead}>
              标记为已读
            </Button>
          )}
        </Space>
      </div>

      <Card>
        {/* 通知头部信息 */}
        <div style={{ marginBottom: '24px' }}>
          <Title level={3} style={{ marginBottom: '16px' }}>
            {notification.title}
          </Title>
          
          <Space wrap>
            <Tag color={getTypeColor(notification.notification_type)}>
              {getTypeText(notification.notification_type)}
            </Tag>
            <Tag color={getPriorityColor(notification.priority)}>
              优先级: {getPriorityText(notification.priority)}
            </Tag>
          </Space>
        </div>

        {/* 基本信息 */}
        <Descriptions bordered column={2} style={{ marginBottom: '24px' }}>
          <Descriptions.Item label="发送者" span={1}>
            <Space>
              <UserOutlined />
              {notification.sender_full_name || notification.sender_name || '系统'}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="发送时间" span={1}>
            <Space>
              <ClockCircleOutlined />
              {dayjs(notification.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="通知类型" span={1}>
            {getTypeText(notification.notification_type)}
          </Descriptions.Item>
          <Descriptions.Item label="阅读状态" span={1}>
            {notification.is_read ? (
              <Tag color="green">已读</Tag>
            ) : (
              <Tag color="red">未读</Tag>
            )}
          </Descriptions.Item>
        </Descriptions>

        {/* 通知内容 */}
        <div style={{ marginBottom: '24px' }}>
          <Title level={4}>通知内容</Title>
          <div style={{
            backgroundColor: '#fafafa',
            padding: '16px',
            borderRadius: '6px',
            border: '1px solid #f0f0f0',
          }}>
            <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
              {notification.message}
            </Paragraph>
          </div>
        </div>

        {/* 额外数据 */}
        {notification.extra_data && Object.keys(notification.extra_data).length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <Title level={4}>相关信息</Title>
            <div style={{
              backgroundColor: '#f9f9f9',
              padding: '16px',
              borderRadius: '6px',
              border: '1px solid #f0f0f0',
            }}>
              <pre style={{ margin: 0, fontSize: '12px' }}>
                {JSON.stringify(notification.extra_data, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* 重要通知提醒 */}
        {(notification.priority === 'urgent' || notification.priority === 'high') && (
          <>
            <Divider />
            <Alert
              message={notification.priority === 'urgent' ? '紧急通知' : '重要通知'}
              description={`这是一条${getPriorityText(notification.priority)}优先级通知，请及时关注并采取相应行动。`}
              type={notification.priority === 'urgent' ? 'error' : 'warning'}
              showIcon
            />
          </>
        )}
      </Card>
    </div>
  );
};

export default NotificationDetailPage;

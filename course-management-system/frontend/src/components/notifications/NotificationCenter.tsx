import React, { useState, useEffect } from 'react';
import {
  Drawer,
  List,
  Badge,
  Button,
  Typography,
  Space,
  Tag,
  Empty,
  Spin,
  Divider,
  Tooltip,
  Avatar
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  SettingOutlined,
  ReloadOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { useNotificationWebSocket } from '../../hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const { Title, Text, Paragraph } = Typography;

interface NotificationCenterProps {
  visible: boolean;
  onClose: () => void;
  className?: string;
}

interface NotificationItem {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  read_at?: string;
  extra_data?: any;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  visible,
  onClose,
  className = ''
}) => {
  const [loading, setLoading] = useState(false);
  const [selectedNotifications, setSelectedNotifications] = useState<number[]>([]);
  
  const {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    getNotifications
  } = useNotificationWebSocket();

  // 获取通知类型的显示信息
  const getNotificationTypeInfo = (type: string) => {
    const typeMap: { [key: string]: { color: string; label: string } } = {
      'course_enrollment': { color: 'blue', label: '选课' },
      'grade_published': { color: 'green', label: '成绩' },
      'assignment_due': { color: 'orange', label: '作业' },
      'schedule_change': { color: 'purple', label: '课表' },
      'system_announcement': { color: 'red', label: '公告' },
      'course_reminder': { color: 'cyan', label: '提醒' },
      'exam_notification': { color: 'magenta', label: '考试' }
    };
    return typeMap[type] || { color: 'default', label: '通知' };
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    const priorityMap: { [key: string]: string } = {
      'urgent': '#ff4d4f',
      'high': '#fa8c16',
      'normal': '#1890ff',
      'low': '#52c41a'
    };
    return priorityMap[priority] || '#1890ff';
  };

  // 处理通知点击
  const handleNotificationClick = (notification: NotificationItem) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    
    // 根据通知类型执行相应操作
    if (notification.extra_data?.url) {
      window.open(notification.extra_data.url, '_blank');
    }
  };

  // 标记所有为已读
  const markAllAsRead = () => {
    const unreadNotifications = notifications.filter(n => !n.is_read);
    unreadNotifications.forEach(notification => {
      markAsRead(notification.id);
    });
  };

  // 刷新通知
  const refreshNotifications = () => {
    setLoading(true);
    getNotifications(1, 50);
    setTimeout(() => setLoading(false), 1000);
  };

  // 渲染通知项
  const renderNotificationItem = (notification: NotificationItem) => {
    const typeInfo = getNotificationTypeInfo(notification.notification_type);
    const isUnread = !notification.is_read;
    
    return (
      <List.Item
        key={notification.id}
        className={`notification-item ${isUnread ? 'unread' : 'read'}`}
        style={{
          backgroundColor: isUnread ? '#f6ffed' : 'transparent',
          borderLeft: isUnread ? `3px solid ${getPriorityColor(notification.priority)}` : 'none',
          cursor: 'pointer',
          padding: '12px 16px'
        }}
        onClick={() => handleNotificationClick(notification)}
        actions={[
          <Tooltip title={isUnread ? "标记为已读" : "已读"}>
            <Button
              type="text"
              size="small"
              icon={<CheckOutlined />}
              style={{ 
                color: isUnread ? '#1890ff' : '#52c41a',
                opacity: isUnread ? 1 : 0.5
              }}
              onClick={(e) => {
                e.stopPropagation();
                if (isUnread) {
                  markAsRead(notification.id);
                }
              }}
            />
          </Tooltip>
        ]}
      >
        <List.Item.Meta
          avatar={
            <Avatar
              style={{ 
                backgroundColor: getPriorityColor(notification.priority),
                color: 'white'
              }}
              size="small"
            >
              {typeInfo.label[0]}
            </Avatar>
          }
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text strong={isUnread} style={{ flex: 1 }}>
                {notification.title}
              </Text>
              <Tag color={typeInfo.color} size="small">
                {typeInfo.label}
              </Tag>
              {isUnread && (
                <Badge status="processing" />
              )}
            </div>
          }
          description={
            <div>
              <Paragraph
                ellipsis={{ rows: 2 }}
                style={{ 
                  margin: '4px 0',
                  color: isUnread ? '#262626' : '#8c8c8c'
                }}
              >
                {notification.message}
              </Paragraph>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {formatDistanceToNow(new Date(notification.created_at), {
                  addSuffix: true,
                  locale: zhCN
                })}
              </Text>
            </div>
          }
        />
      </List.Item>
    );
  };

  return (
    <Drawer
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Space>
            <BellOutlined />
            <span>通知中心</span>
            {unreadCount > 0 && (
              <Badge count={unreadCount} size="small" />
            )}
            {!isConnected && (
              <Tag color="red" size="small">离线</Tag>
            )}
          </Space>
          <Space>
            <Tooltip title="刷新">
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={refreshNotifications}
                loading={loading}
              />
            </Tooltip>
            <Tooltip title="设置">
              <Button
                type="text"
                size="small"
                icon={<SettingOutlined />}
              />
            </Tooltip>
          </Space>
        </div>
      }
      placement="right"
      width={400}
      open={visible}
      onClose={onClose}
      className={className}
      extra={
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClose}
        />
      }
    >
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Text type="secondary">
            {notifications.length > 0 ? `共 ${notifications.length} 条通知` : '暂无通知'}
          </Text>
          {unreadCount > 0 && (
            <Button
              type="link"
              size="small"
              onClick={markAllAsRead}
            >
              全部标记为已读
            </Button>
          )}
        </Space>
      </div>

      <Divider style={{ margin: '8px 0' }} />

      <Spin spinning={loading}>
        {notifications.length > 0 ? (
          <List
            dataSource={notifications}
            renderItem={renderNotificationItem}
            style={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无通知"
            style={{ marginTop: 60 }}
          />
        )}
      </Spin>

      {notifications.length > 20 && (
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Button
            type="link"
            onClick={() => getNotifications(1, notifications.length + 20)}
          >
            加载更多
          </Button>
        </div>
      )}
    </Drawer>
  );
};

export default NotificationCenter;

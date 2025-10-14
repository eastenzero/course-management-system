import React, { useState } from 'react';
import { Badge, Button, Tooltip, Popover, List, Typography, Space, Tag } from 'antd';
import { BellOutlined, BellFilled } from '@ant-design/icons';
import { useNotificationWebSocket } from '../../hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import NotificationCenter from './NotificationCenter';

const { Text } = Typography;

interface NotificationBellProps {
  size?: 'small' | 'middle' | 'large';
  showQuickPreview?: boolean;
  maxPreviewItems?: number;
  className?: string;
  style?: React.CSSProperties;
}

const NotificationBell: React.FC<NotificationBellProps> = ({
  size = 'middle',
  showQuickPreview = true,
  maxPreviewItems = 5,
  className = '',
  style = {}
}) => {
  const [centerVisible, setCenterVisible] = useState(false);
  const [popoverVisible, setPopoverVisible] = useState(false);

  const {
    notifications,
    unreadCount,
    isConnected,
    markAsRead
  } = useNotificationWebSocket();

  // 获取最近的通知用于快速预览
  const recentNotifications = notifications.slice(0, maxPreviewItems);

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

  // 处理通知点击
  const handleNotificationClick = (notification: any) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    setPopoverVisible(false);
    
    // 根据通知类型执行相应操作
    if (notification.extra_data?.url) {
      window.open(notification.extra_data.url, '_blank');
    }
  };

  // 渲染快速预览内容
  const renderQuickPreview = () => {
    if (!showQuickPreview || recentNotifications.length === 0) {
      return (
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Text type="secondary">暂无新通知</Text>
        </div>
      );
    }

    return (
      <div style={{ width: 320, maxHeight: 400, overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Text strong>最新通知</Text>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setPopoverVisible(false);
                setCenterVisible(true);
              }}
            >
              查看全部
            </Button>
          </Space>
        </div>
        
        <List
          dataSource={recentNotifications}
          renderItem={(notification) => {
            const typeInfo = getNotificationTypeInfo(notification.notification_type);
            const isUnread = !notification.is_read;
            
            return (
              <List.Item
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  backgroundColor: isUnread ? '#f6ffed' : 'transparent',
                  borderLeft: isUnread ? '3px solid #1890ff' : 'none'
                }}
                onClick={() => handleNotificationClick(notification)}
              >
                <List.Item.Meta
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Text
                        strong={isUnread}
                        ellipsis
                        style={{ flex: 1, fontSize: 14 }}
                      >
                        {notification.title}
                      </Text>
                      <Tag color={typeInfo.color} size="small">
                        {typeInfo.label}
                      </Tag>
                    </div>
                  }
                  description={
                    <div>
                      <Text
                        type="secondary"
                        ellipsis={{ rows: 2 }}
                        style={{ fontSize: 12, display: 'block', marginBottom: 4 }}
                      >
                        {notification.message}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 11 }}>
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
          }}
        />
        
        {notifications.length > maxPreviewItems && (
          <div style={{ padding: '8px 16px', textAlign: 'center', borderTop: '1px solid #f0f0f0' }}>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setPopoverVisible(false);
                setCenterVisible(true);
              }}
            >
              查看更多 ({notifications.length - maxPreviewItems} 条)
            </Button>
          </div>
        )}
      </div>
    );
  };

  // 获取铃铛图标
  const getBellIcon = () => {
    if (unreadCount > 0) {
      return <BellFilled style={{ color: '#1890ff' }} />;
    }
    return <BellOutlined />;
  };

  // 获取连接状态提示
  const getConnectionTooltip = () => {
    if (!isConnected) {
      return '通知服务离线';
    }
    if (unreadCount > 0) {
      return `您有 ${unreadCount} 条未读通知`;
    }
    return '暂无新通知';
  };

  return (
    <>
      <Popover
        content={renderQuickPreview()}
        trigger="click"
        placement="bottomRight"
        open={popoverVisible}
        onOpenChange={setPopoverVisible}
        overlayClassName="notification-bell-popover"
      >
        <Tooltip title={getConnectionTooltip()}>
          <Badge
            count={unreadCount}
            size="small"
            offset={[-2, 2]}
            className={className}
            style={style}
          >
            <Button
              type="text"
              icon={getBellIcon()}
              size={size}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: isConnected ? 1 : 0.5
              }}
              onClick={() => {
                if (showQuickPreview && recentNotifications.length > 0) {
                  setPopoverVisible(!popoverVisible);
                } else {
                  setCenterVisible(true);
                }
              }}
            />
          </Badge>
        </Tooltip>
      </Popover>

      <NotificationCenter
        visible={centerVisible}
        onClose={() => setCenterVisible(false)}
      />
    </>
  );
};

export default NotificationBell;

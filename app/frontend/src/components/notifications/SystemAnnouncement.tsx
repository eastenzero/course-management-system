import React, { useState, useEffect } from 'react';
import {
  Alert,
  Modal,
  Button,
  Typography,
  Space,
  Tag,
  Divider,
  List,
  Card,
  Badge
} from 'antd';
import {
  SoundOutlined,
  CloseOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useSystemNotificationWebSocket } from '../../hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const { Title, Text, Paragraph } = Typography;

interface SystemAnnouncementProps {
  showFloatingAlert?: boolean;
  maxFloatingAlerts?: number;
  autoHideDelay?: number;
  className?: string;
}

interface SystemNotification {
  id?: string;
  title: string;
  message: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  timestamp: string;
  type?: 'announcement' | 'maintenance' | 'warning';
}

const SystemAnnouncement: React.FC<SystemAnnouncementProps> = ({
  showFloatingAlert = true,
  maxFloatingAlerts = 3,
  autoHideDelay = 10000,
  className = ''
}) => {
  const [floatingAlerts, setFloatingAlerts] = useState<SystemNotification[]>([]);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  const { systemNotifications, isConnected } = useSystemNotificationWebSocket();

  // 处理新的系统通知
  useEffect(() => {
    if (systemNotifications.length > 0) {
      const latestNotification = systemNotifications[0];
      
      // 添加到浮动提醒
      if (showFloatingAlert && !dismissedAlerts.has(latestNotification.id || latestNotification.timestamp)) {
        setFloatingAlerts(prev => {
          const newAlerts = [latestNotification, ...prev].slice(0, maxFloatingAlerts);
          return newAlerts;
        });

        // 自动隐藏（除非是紧急通知）
        if (latestNotification.priority !== 'urgent' && autoHideDelay > 0) {
          setTimeout(() => {
            dismissAlert(latestNotification.id || latestNotification.timestamp);
          }, autoHideDelay);
        }
      }
    }
  }, [systemNotifications, showFloatingAlert, maxFloatingAlerts, autoHideDelay, dismissedAlerts]);

  // 获取优先级配置
  const getPriorityConfig = (priority: string) => {
    const configs = {
      urgent: {
        type: 'error' as const,
        icon: <ExclamationCircleOutlined />,
        color: '#ff4d4f',
        label: '紧急'
      },
      high: {
        type: 'warning' as const,
        icon: <WarningOutlined />,
        color: '#fa8c16',
        label: '重要'
      },
      normal: {
        type: 'info' as const,
        icon: <InfoCircleOutlined />,
        color: '#1890ff',
        label: '普通'
      },
      low: {
        type: 'success' as const,
        icon: <InfoCircleOutlined />,
        color: '#52c41a',
        label: '一般'
      }
    };
    return configs[priority as keyof typeof configs] || configs.normal;
  };

  // 获取通知类型配置
  const getTypeConfig = (type?: string) => {
    const configs = {
      maintenance: {
        color: 'orange',
        label: '系统维护'
      },
      warning: {
        color: 'red',
        label: '警告'
      },
      announcement: {
        color: 'blue',
        label: '公告'
      }
    };
    return configs[type as keyof typeof configs] || configs.announcement;
  };

  // 关闭浮动提醒
  const dismissAlert = (id: string) => {
    setFloatingAlerts(prev => prev.filter(alert => (alert.id || alert.timestamp) !== id));
    setDismissedAlerts(prev => new Set([...prev, id]));
  };

  // 渲染浮动提醒
  const renderFloatingAlerts = () => {
    if (!showFloatingAlert || floatingAlerts.length === 0) {
      return null;
    }

    return (
      <div
        style={{
          position: 'fixed',
          top: 80,
          right: 24,
          zIndex: 1000,
          maxWidth: 400,
          width: '100%'
        }}
        className={className}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {floatingAlerts.map((notification) => {
            const priorityConfig = getPriorityConfig(notification.priority);
            const typeConfig = getTypeConfig(notification.type);
            const alertId = notification.id || notification.timestamp;

            return (
              <Alert
                key={alertId}
                type={priorityConfig.type}
                showIcon
                icon={priorityConfig.icon}
                message={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <SoundOutlined style={{ color: priorityConfig.color }} />
                    <Text strong>{notification.title}</Text>
                    <Tag color={typeConfig.color} size="small">
                      {typeConfig.label}
                    </Tag>
                    <Tag color={priorityConfig.color} size="small">
                      {priorityConfig.label}
                    </Tag>
                  </div>
                }
                description={
                  <div style={{ marginTop: 8 }}>
                    <Paragraph style={{ margin: 0, marginBottom: 8 }}>
                      {notification.message}
                    </Paragraph>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {formatDistanceToNow(new Date(notification.timestamp), {
                        addSuffix: true,
                        locale: zhCN
                      })}
                    </Text>
                  </div>
                }
                action={
                  <Space>
                    <Button
                      size="small"
                      type="link"
                      onClick={() => setHistoryVisible(true)}
                    >
                      查看历史
                    </Button>
                    <Button
                      size="small"
                      type="text"
                      icon={<CloseOutlined />}
                      onClick={() => dismissAlert(alertId)}
                    />
                  </Space>
                }
                closable={false}
                style={{
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                  border: `1px solid ${priorityConfig.color}`,
                  borderRadius: 6
                }}
              />
            );
          })}
        </Space>
      </div>
    );
  };

  // 渲染历史记录模态框
  const renderHistoryModal = () => (
    <Modal
      title={
        <Space>
          <SoundOutlined />
          系统公告历史
          <Badge
            count={systemNotifications.length}
            style={{ backgroundColor: '#1890ff' }}
          />
        </Space>
      }
      open={historyVisible}
      onCancel={() => setHistoryVisible(false)}
      footer={[
        <Button key="close" onClick={() => setHistoryVisible(false)}>
          关闭
        </Button>
      ]}
      width={600}
      style={{ top: 50 }}
    >
      {systemNotifications.length > 0 ? (
        <List
          dataSource={systemNotifications}
          renderItem={(notification, index) => {
            const priorityConfig = getPriorityConfig(notification.priority);
            const typeConfig = getTypeConfig(notification.type);

            return (
              <List.Item key={index}>
                <Card
                  size="small"
                  style={{
                    width: '100%',
                    borderLeft: `4px solid ${priorityConfig.color}`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    {priorityConfig.icon}
                    <Title level={5} style={{ margin: 0, flex: 1 }}>
                      {notification.title}
                    </Title>
                    <Tag color={typeConfig.color} size="small">
                      {typeConfig.label}
                    </Tag>
                    <Tag color={priorityConfig.color} size="small">
                      {priorityConfig.label}
                    </Tag>
                  </div>
                  
                  <Paragraph style={{ margin: 0, marginBottom: 8 }}>
                    {notification.message}
                  </Paragraph>
                  
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {formatDistanceToNow(new Date(notification.timestamp), {
                      addSuffix: true,
                      locale: zhCN
                    })}
                  </Text>
                </Card>
              </List.Item>
            );
          }}
          style={{ maxHeight: 400, overflowY: 'auto' }}
        />
      ) : (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Text type="secondary">暂无系统公告</Text>
        </div>
      )}
    </Modal>
  );

  return (
    <>
      {renderFloatingAlerts()}
      {renderHistoryModal()}
      
      {/* 连接状态指示器 */}
      {!isConnected && (
        <div
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 999
          }}
        >
          <Alert
            type="warning"
            message="系统通知服务离线"
            description="无法接收实时系统公告"
            showIcon
            closable
            style={{
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
          />
        </div>
      )}
    </>
  );
};

export default SystemAnnouncement;

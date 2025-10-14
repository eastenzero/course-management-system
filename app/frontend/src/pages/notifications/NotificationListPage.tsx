import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  List,
  Card,
  Button,
  Space,
  Tag,
  Badge,
  Empty,
  Row,
  Col,
  Select,
  Input,
  Checkbox,
  message,
  Popconfirm,
  Spin,
} from 'antd';
import {
  BellOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  CheckOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { notificationAPI } from '../../services/api';

dayjs.extend(relativeTime);

const { Title } = Typography;
const { Option } = Select;

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

const NotificationListPage: React.FC = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [filterType, setFilterType] = useState<string>('');
  const [filterPriority, setFilterPriority] = useState<string>('');
  const [searchText, setSearchText] = useState('');
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 获取通知列表
  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };

      if (showUnreadOnly) {
        params.is_read = false;
      }
      if (filterType) {
        params.type = filterType;
      }
      if (filterPriority) {
        params.priority = filterPriority;
      }

      const response = await notificationAPI.getNotifications(params);
      setNotifications(response.data.results || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.count || 0,
      }));
    } catch (error) {
      console.error('获取通知列表失败:', error);
      message.error('获取通知列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [pagination.current, pagination.pageSize, showUnreadOnly, filterType, filterPriority]);

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

  const handleNotificationClick = async (notification: Notification) => {
    // 如果未读，先标记为已读
    if (!notification.is_read) {
      try {
        await notificationAPI.markAsRead([notification.id]);
        setNotifications(prev =>
          prev.map(n =>
            n.id === notification.id ? { ...n, is_read: true } : n
          )
        );
      } catch (error) {
        console.error('标记已读失败:', error);
      }
    }
    navigate(`/notifications/${notification.id}`);
  };

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationAPI.markAsRead([id]);
      setNotifications(prev =>
        prev.map(n =>
          n.id === id ? { ...n, is_read: true } : n
        )
      );
      message.success('已标记为已读');
    } catch (error) {
      console.error('标记已读失败:', error);
      message.error('标记已读失败');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead();
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true }))
      );
      message.success('已全部标记为已读');
    } catch (error) {
      console.error('标记全部已读失败:', error);
      message.error('标记全部已读失败');
    }
  };

  const handleBatchMarkAsRead = async () => {
    try {
      await notificationAPI.markAsRead(selectedIds);
      setNotifications(prev =>
        prev.map(n =>
          selectedIds.includes(n.id) ? { ...n, is_read: true } : n
        )
      );
      setSelectedIds([]);
      message.success('批量标记为已读');
    } catch (error) {
      console.error('批量标记已读失败:', error);
      message.error('批量标记已读失败');
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = notification.title.toLowerCase().includes(searchText.toLowerCase()) ||
                         notification.message.toLowerCase().includes(searchText.toLowerCase());
    const matchesType = !filterType || notification.notification_type === filterType;
    const matchesPriority = !filterPriority || notification.priority === filterPriority;
    const matchesReadStatus = !showUnreadOnly || !notification.is_read;

    return matchesSearch && matchesType && matchesPriority && matchesReadStatus;
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notification-list-page">
      <div className="page-header">
        <Title level={2}>
          <Space>
            <BellOutlined />
            <span>通知中心</span>
            {unreadCount > 0 && (
              <Badge count={unreadCount} style={{ backgroundColor: '#ff4d4f' }} />
            )}
          </Space>
        </Title>
        <p>查看系统通知和消息</p>
      </div>

      <Card>
        {/* 筛选和搜索 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8} md={6}>
            <Input
              placeholder="搜索通知标题或内容"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="通知类型"
              style={{ width: '100%' }}
              value={filterType}
              onChange={setFilterType}
              allowClear
            >
              <Option value="course_enrollment">课程选课</Option>
              <Option value="grade_published">成绩发布</Option>
              <Option value="assignment_due">作业截止</Option>
              <Option value="schedule_change">课程表变更</Option>
              <Option value="system_announcement">系统公告</Option>
              <Option value="course_reminder">课程提醒</Option>
              <Option value="exam_notification">考试通知</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="优先级"
              style={{ width: '100%' }}
              value={filterPriority}
              onChange={setFilterPriority}
              allowClear
            >
              <Option value="urgent">紧急</Option>
              <Option value="high">高</Option>
              <Option value="normal">普通</Option>
              <Option value="low">低</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={10}>
            <Space>
              <Checkbox
                checked={showUnreadOnly}
                onChange={(e) => setShowUnreadOnly(e.target.checked)}
              >
                仅显示未读
              </Checkbox>
              <Button onClick={handleMarkAllAsRead}>
                全部标记为已读
              </Button>
              {selectedIds.length > 0 && (
                <>
                  <Button onClick={handleBatchMarkAsRead}>
                    批量标记已读
                  </Button>
                  <Popconfirm
                    title="确定删除选中的通知吗？"
                    onConfirm={handleBatchDelete}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button danger>
                      批量删除
                    </Button>
                  </Popconfirm>
                </>
              )}
            </Space>
          </Col>
        </Row>

        {/* 通知列表 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" tip="加载中..." />
          </div>
        ) : filteredNotifications.length === 0 ? (
          <Empty description="暂无通知" />
        ) : (
          <List
            dataSource={filteredNotifications}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              onChange: (page, pageSize) => {
                setPagination(prev => ({
                  ...prev,
                  current: page,
                  pageSize: pageSize || 20,
                }));
              },
            }}
            renderItem={(notification) => (
              <List.Item
                key={notification.id}
                style={{
                  backgroundColor: notification.is_read ? '#fff' : '#f6ffed',
                  border: notification.is_read ? '1px solid #f0f0f0' : '1px solid #b7eb8f',
                  borderRadius: '6px',
                  marginBottom: '8px',
                  padding: '16px',
                }}
                actions={[
                  <Checkbox
                    key="select"
                    checked={selectedIds.includes(notification.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedIds([...selectedIds, notification.id]);
                      } else {
                        setSelectedIds(selectedIds.filter(id => id !== notification.id));
                      }
                    }}
                  />,
                  <Button
                    key="view"
                    type="link"
                    icon={<EyeOutlined />}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    查看
                  </Button>,
                  !notification.is_read && (
                    <Button
                      key="read"
                      type="link"
                      onClick={() => handleMarkAsRead(notification.id)}
                    >
                      标记已读
                    </Button>
                  ),
                ].filter(Boolean)}
              >
                <List.Item.Meta
                  avatar={
                    <div style={{ position: 'relative' }}>
                      {getTypeIcon(notification.notification_type)}
                      {!notification.is_read && (
                        <Badge
                          dot
                          style={{
                            position: 'absolute',
                            top: '-2px',
                            right: '-2px',
                          }}
                        />
                      )}
                    </div>
                  }
                  title={
                    <div
                      style={{
                        cursor: 'pointer',
                        fontWeight: notification.is_read ? 'normal' : 'bold',
                      }}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <Space>
                        <span>{notification.title}</span>
                        <Tag color={getTypeColor(notification.notification_type)} size="small">
                          {getTypeText(notification.notification_type)}
                        </Tag>
                        <Tag color={getPriorityColor(notification.priority)} size="small">
                          {getPriorityText(notification.priority)}
                        </Tag>
                      </Space>
                    </div>
                  }
                  description={
                    <div>
                      <div style={{
                        marginBottom: '8px',
                        color: notification.is_read ? '#666' : '#333'
                      }}>
                        {notification.message.length > 100
                          ? `${notification.message.substring(0, 100)}...`
                          : notification.message
                        }
                      </div>
                      <Space size="small">
                        {notification.sender_full_name && (
                          <span style={{ fontSize: '12px', color: '#999' }}>
                            来自: {notification.sender_full_name}
                          </span>
                        )}
                        <span style={{ fontSize: '12px', color: '#999' }}>
                          <ClockCircleOutlined style={{ marginRight: '4px' }} />
                          {notification.time_since_created}
                        </span>
                      </Space>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default NotificationListPage;

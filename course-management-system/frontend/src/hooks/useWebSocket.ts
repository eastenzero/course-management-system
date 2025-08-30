import { useEffect, useRef, useState, useCallback } from 'react';
import { message } from 'antd';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  autoConnect?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
}

export const useWebSocket = (
  url: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    autoConnect = true
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    
    try {
      // 获取认证token
      const token = localStorage.getItem('access_token');
      const wsUrl = token ? `${url}?token=${token}` : url;
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        reconnectCountRef.current = 0;
        onConnect?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const messageData = JSON.parse(event.data);
          setLastMessage(messageData);
          onMessage?.(messageData);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        setIsConnecting(false);
        onDisconnect?.();

        // 自动重连
        if (shouldReconnectRef.current && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        setIsConnecting(false);
        onError?.(error);
      };

    } catch (error) {
      setIsConnecting(false);
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, reconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((messageData: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(messageData));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, autoConnect]);

  return {
    isConnected,
    isConnecting,
    sendMessage,
    connect,
    disconnect,
    lastMessage
  };
};

// 通知WebSocket Hook
export const useNotificationWebSocket = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'connection_established':
        console.log('Notification WebSocket connected');
        break;
        
      case 'new_notification':
        setNotifications(prev => [message.notification, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // 显示通知提示
        message.info({
          content: message.notification.title,
          duration: 4,
        });
        break;
        
      case 'unread_count':
        setUnreadCount(message.count);
        break;
        
      case 'notification_read':
        setUnreadCount(message.unread_count);
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === message.notification_id 
              ? { ...notif, is_read: true }
              : notif
          )
        );
        break;
        
      case 'notifications_list':
        setNotifications(message.notifications);
        break;
        
      case 'error':
        console.error('Notification WebSocket error:', message.message);
        break;
        
      default:
        console.log('Unknown notification message type:', message.type);
    }
  }, []);

  const wsUrl = `ws://${window.location.host}/ws/notifications/`;
  
  const { isConnected, sendMessage } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
    onConnect: () => {
      console.log('Connected to notification WebSocket');
      // 请求获取通知列表
      sendMessage({ type: 'get_notifications', page: 1, page_size: 20 });
    },
    onDisconnect: () => {
      console.log('Disconnected from notification WebSocket');
    }
  });

  const markAsRead = useCallback((notificationId: number) => {
    sendMessage({
      type: 'mark_as_read',
      notification_id: notificationId
    });
  }, [sendMessage]);

  const getNotifications = useCallback((page: number = 1, pageSize: number = 20) => {
    sendMessage({
      type: 'get_notifications',
      page,
      page_size: pageSize
    });
  }, [sendMessage]);

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    getNotifications
  };
};

// 系统通知WebSocket Hook
export const useSystemNotificationWebSocket = () => {
  const [systemNotifications, setSystemNotifications] = useState<any[]>([]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'system_announcement':
        setSystemNotifications(prev => [message.announcement, ...prev]);
        
        // 显示系统公告
        message.warning({
          content: `系统公告: ${message.announcement.title}`,
          duration: 6,
        });
        break;
        
      case 'system_maintenance':
        // 显示系统维护通知
        message.error({
          content: `系统维护: ${message.maintenance.title}`,
          duration: 0, // 不自动关闭
        });
        break;
        
      default:
        console.log('Unknown system notification message type:', message.type);
    }
  }, []);

  const wsUrl = `ws://${window.location.host}/ws/system-notifications/`;
  
  const { isConnected } = useWebSocket(wsUrl, {
    onMessage: handleMessage
  });

  return {
    systemNotifications,
    isConnected
  };
};

// 课程通知WebSocket Hook
export const useCourseNotificationWebSocket = (courseId: number) => {
  const [courseNotifications, setCourseNotifications] = useState<any[]>([]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'course_update':
        setCourseNotifications(prev => [message.update, ...prev]);
        message.info(`课程更新: ${message.update.title}`);
        break;
        
      case 'grade_published':
        setCourseNotifications(prev => [message.grade, ...prev]);
        message.success(`成绩发布: ${message.grade.title}`);
        break;
        
      case 'schedule_change':
        setCourseNotifications(prev => [message.change, ...prev]);
        message.warning(`课程表变更: ${message.change.title}`);
        break;
        
      default:
        console.log('Unknown course notification message type:', message.type);
    }
  }, []);

  const wsUrl = `ws://${window.location.host}/ws/course-notifications/${courseId}/`;
  
  const { isConnected } = useWebSocket(wsUrl, {
    onMessage: handleMessage
  });

  return {
    courseNotifications,
    isConnected
  };
};

export default useWebSocket;

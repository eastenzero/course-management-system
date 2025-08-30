import React from 'react';
import { Avatar, Badge, Tooltip, Space } from 'antd';
import { 
  UserOutlined, 
  CrownOutlined, 
  BookOutlined,
  TeamOutlined 
} from '@ant-design/icons';

interface User {
  id: string;
  username: string;
  firstName: string;
  lastName: string;
  userType: 'admin' | 'teacher' | 'student';
  avatar?: string;
  isOnline?: boolean;
}

interface UserAvatarProps {
  user: User;
  size?: 'small' | 'default' | 'large' | number;
  showName?: boolean;
  showRole?: boolean;
  showOnlineStatus?: boolean;
  onClick?: (user: User) => void;
  style?: React.CSSProperties;
}

const UserAvatar: React.FC<UserAvatarProps> = ({
  user,
  size = 'default',
  showName = false,
  showRole = false,
  showOnlineStatus = false,
  onClick,
  style,
}) => {
  const getRoleIcon = (userType: string) => {
    switch (userType) {
      case 'admin':
        return <CrownOutlined style={{ color: '#ff4d4f' }} />;
      case 'teacher':
        return <BookOutlined style={{ color: '#1890ff' }} />;
      case 'student':
        return <TeamOutlined style={{ color: '#52c41a' }} />;
      default:
        return null;
    }
  };

  const getRoleText = (userType: string) => {
    switch (userType) {
      case 'admin':
        return '管理员';
      case 'teacher':
        return '教师';
      case 'student':
        return '学生';
      default:
        return '';
    }
  };

  const getRoleColor = (userType: string) => {
    switch (userType) {
      case 'admin':
        return '#ff4d4f';
      case 'teacher':
        return '#1890ff';
      case 'student':
        return '#52c41a';
      default:
        return '#666';
    }
  };

  const getAvatarSize = () => {
    if (typeof size === 'number') return size;
    switch (size) {
      case 'small':
        return 24;
      case 'large':
        return 40;
      default:
        return 32;
    }
  };

  const getNameFontSize = () => {
    if (typeof size === 'number') {
      if (size <= 24) return '12px';
      if (size >= 40) return '16px';
      return '14px';
    }
    switch (size) {
      case 'small':
        return '12px';
      case 'large':
        return '16px';
      default:
        return '14px';
    }
  };

  const generateColorFromName = (name: string) => {
    const colors = [
      '#f56a00', '#7265e6', '#ffbf00', '#00a2ae',
      '#1890ff', '#52c41a', '#fa8c16', '#eb2f96',
      '#722ed1', '#13c2c2', '#fa541c', '#2f54eb',
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const fullName = `${user.lastName}${user.firstName}`;
  const avatarColor = generateColorFromName(fullName);

  const avatarElement = (
    <Avatar
      size={getAvatarSize()}
      src={user.avatar}
      style={{
        backgroundColor: user.avatar ? undefined : avatarColor,
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
      onClick={() => onClick?.(user)}
    >
      {user.avatar ? null : (fullName.charAt(0) || <UserOutlined />)}
    </Avatar>
  );

  const avatarWithBadge = showOnlineStatus ? (
    <Badge
      dot
      status={user.isOnline ? 'success' : 'default'}
      offset={[-2, getAvatarSize() - 8]}
    >
      {avatarElement}
    </Badge>
  ) : (
    avatarElement
  );

  if (!showName && !showRole) {
    return (
      <Tooltip title={`${fullName} (${getRoleText(user.userType)})`}>
        {avatarWithBadge}
      </Tooltip>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        cursor: onClick ? 'pointer' : 'default',
      }}
      onClick={() => onClick?.(user)}
    >
      {avatarWithBadge}
      
      {(showName || showRole) && (
        <div style={{ marginLeft: '8px', minWidth: 0 }}>
          {showName && (
            <div
              style={{
                fontSize: getNameFontSize(),
                fontWeight: '500',
                color: '#262626',
                lineHeight: '1.2',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {fullName}
            </div>
          )}
          
          {showRole && (
            <div
              style={{
                fontSize: '12px',
                color: getRoleColor(user.userType),
                lineHeight: '1.2',
                marginTop: showName ? '2px' : '0',
              }}
            >
              <Space size={4}>
                {getRoleIcon(user.userType)}
                <span>{getRoleText(user.userType)}</span>
              </Space>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserAvatar;

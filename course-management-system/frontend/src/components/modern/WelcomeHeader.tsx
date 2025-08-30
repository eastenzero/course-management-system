import React from 'react';
import { Avatar } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import '../../styles/modern.css';

interface WelcomeHeaderProps {
  userType: 'teacher' | 'student';
  userName: string;
  userInfo: {
    avatar?: string;
    id?: string;
    email?: string;
    title?: string;
    major?: string;
    className?: string;
  };
  todayStats?: {
    courses?: number;
    tasks?: number;
  };
}

const WelcomeHeader: React.FC<WelcomeHeaderProps> = ({ 
  userType, 
  userName, 
  userInfo,
  todayStats = {}
}) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return '早上好';
    if (hour < 18) return '下午好';
    return '晚上好';
  };

  const getMotivationalText = () => {
    if (userType === 'teacher') {
      return '今天又是充满教学热情的一天！';
    }
    return '今天也要努力学习哦！';
  };

  const getFloatingElements = () => {
    if (userType === 'teacher') {
      return ['📚', '✨', '🎓'];
    }
    return ['📖', '⭐', '🌟'];
  };

  const elements = getFloatingElements();

  return (
    <div className={`welcome-header ${userType}-theme fade-in`}>
      <div className="welcome-background">
        <div className="gradient-overlay"></div>
        <div className="floating-elements">
          {elements.map((element, index) => (
            <div key={index} className={`element element-${index + 1}`}>
              {element}
            </div>
          ))}
        </div>
      </div>
      
      <div className="welcome-content">
        <div className="avatar-section">
          <div className="avatar-container">
            <Avatar 
              size={80} 
              src={userInfo.avatar} 
              icon={<UserOutlined />}
              style={{ 
                border: '4px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
              }}
            />
            <div className="online-indicator"></div>
          </div>
        </div>
        
        <div className="greeting-section">
          <h2 className="greeting-text">
            {getGreeting()}，{userName}！
          </h2>
          <p className="motivational-text">
            {getMotivationalText()}
          </p>
          
          {/* 用户信息 */}
          <div style={{ marginBottom: '12px', opacity: 0.9 }}>
            {userType === 'teacher' ? (
              <>
                <span style={{ fontSize: '14px', marginRight: '16px' }}>
                  工号：{userInfo.id}
                </span>
                {userInfo.title && (
                  <span style={{ fontSize: '14px', marginRight: '16px' }}>
                    职称：{userInfo.title}
                  </span>
                )}
              </>
            ) : (
              <>
                <span style={{ fontSize: '14px', marginRight: '16px' }}>
                  学号：{userInfo.id}
                </span>
                {userInfo.major && (
                  <span style={{ fontSize: '14px', marginRight: '16px' }}>
                    专业：{userInfo.major}
                  </span>
                )}
                {userInfo.className && (
                  <span style={{ fontSize: '14px' }}>
                    班级：{userInfo.className}
                  </span>
                )}
              </>
            )}
          </div>
          
          {/* 今日统计 */}
          <div className="quick-stats">
            {userType === 'teacher' ? (
              <span>今日课程：{todayStats.courses || 0}节</span>
            ) : (
              <span>今日课程：{todayStats.courses || 0}节</span>
            )}
            {todayStats.tasks !== undefined && (
              <span style={{ marginLeft: '12px' }}>
                待办任务：{todayStats.tasks}项
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeHeader;

import React, { useState, useMemo } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, Badge, Space } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  BookOutlined,
  CalendarOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  BellOutlined,
  HomeOutlined,
  BarChartOutlined,
  TeamOutlined,
  EditOutlined,
  TrophyOutlined,
  ReadOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/index';
import type { MenuItem, UserRole } from '../../types/index';
import BreadcrumbNav from '../common/BreadcrumbNav';
import ThemeSelector from '../common/ThemeSelector';
import { useTheme } from '../../hooks/useThemeV2';
import './MainLayout.css';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const { user } = useSelector((state: RootState) => state.auth);
  const { notifications } = useSelector((state: RootState) => state.app);
  const { uiTheme, getThemeColors } = useTheme();

  // 菜单配置
  const menuItems: MenuItem[] = [
    {
      key: '/dashboard',
      label: '仪表板',
      icon: <DashboardOutlined />,
      path: '/dashboard',
      roles: ['admin', 'teacher', 'student'] as UserRole[],
    },
    {
      key: '/courses',
      label: '课程管理',
      icon: <BookOutlined />,
      roles: ['admin', 'teacher'] as UserRole[],
      children: [
        {
          key: '/courses/list',
          label: '课程列表',
          path: '/courses/list',
          roles: ['admin', 'teacher'] as UserRole[],
        },
        {
          key: '/courses/create',
          label: '创建课程',
          path: '/courses/create',
          roles: ['admin', 'teacher'] as UserRole[],
        },
      ],
    },
    {
      key: '/schedules',
      label: '课程表管理',
      icon: <CalendarOutlined />,
      roles: ['admin', 'teacher'] as UserRole[],
      children: [
        {
          key: '/schedules/view',
          label: '查看课程表',
          path: '/schedules/view',
          roles: ['admin', 'teacher', 'student'] as UserRole[],
        },
        {
          key: '/schedules/manage',
          label: '排课管理',
          path: '/schedules/manage',
          roles: ['admin'] as UserRole[],
        },
        {
          key: '/schedules/conflicts',
          label: '冲突检测',
          path: '/schedules/conflicts',
          roles: ['admin'] as UserRole[],
        },
      ],
    },
    {
      key: '/classrooms',
      label: '教室管理',
      icon: <HomeOutlined />,
      roles: ['admin'] as UserRole[],
      children: [
        {
          key: '/classrooms/list',
          label: '教室列表',
          path: '/classrooms/list',
          roles: ['admin'] as UserRole[],
        },
        {
          key: '/classrooms/create',
          label: '添加教室',
          path: '/classrooms/create',
          roles: ['admin'] as UserRole[],
        },
      ],
    },
    {
      key: '/users',
      label: '用户管理',
      icon: <UserOutlined />,
      roles: ['admin'] as UserRole[],
      children: [
        {
          key: '/users/list',
          label: '用户列表',
          path: '/users/list',
          roles: ['admin'] as UserRole[],
        },
        {
          key: '/users/create',
          label: '添加用户',
          path: '/users/create',
          roles: ['admin'] as UserRole[],
        },
      ],
    },
    {
      key: '/analytics',
      label: '数据分析',
      icon: <BarChartOutlined />,
      path: '/analytics',
      roles: ['admin', 'teacher'] as UserRole[],
    },
    // 学生专用菜单
    {
      key: '/students',
      label: '学生中心',
      icon: <ReadOutlined />,
      roles: ['student'] as UserRole[],
      children: [
        {
          key: '/students/dashboard',
          label: '学生仪表板',
          path: '/students/dashboard',
          roles: ['student'] as UserRole[],
        },
        {
          key: '/students/course-selection',
          label: '选课系统',
          path: '/students/course-selection',
          roles: ['student'] as UserRole[],
        },
        {
          key: '/students/my-courses',
          label: '我的课程',
          path: '/students/my-courses',
          roles: ['student'] as UserRole[],
        },
        {
          key: '/students/schedule',
          label: '课程表',
          path: '/students/schedule',
          roles: ['student'] as UserRole[],
        },
        {
          key: '/students/grades',
          label: '成绩查询',
          path: '/students/grades',
          roles: ['student'] as UserRole[],
        },
        {
          key: '/students/profile',
          label: '个人信息',
          path: '/students/profile',
          roles: ['student'] as UserRole[],
        },
      ],
    },
    // 教师专用菜单
    {
      key: '/teachers',
      label: '教师中心',
      icon: <TeamOutlined />,
      roles: ['teacher'] as UserRole[],
      children: [
        {
          key: '/teachers/dashboard',
          label: '教师仪表板',
          path: '/teachers/dashboard',
          roles: ['teacher'] as UserRole[],
        },
        {
          key: '/teachers/my-courses',
          label: '我的课程',
          path: '/teachers/my-courses',
          roles: ['teacher'] as UserRole[],
        },
        {
          key: '/teachers/grade-entry',
          label: '成绩录入',
          path: '/teachers/grade-entry',
          roles: ['teacher'] as UserRole[],
        },
        {
          key: '/teachers/grade-management',
          label: '成绩管理',
          path: '/teachers/grade-management',
          roles: ['teacher'] as UserRole[],
        },
        {
          key: '/teachers/schedule',
          label: '教学安排',
          path: '/teachers/schedule',
          roles: ['teacher'] as UserRole[],
        },
        {
          key: '/teachers/profile',
          label: '个人信息',
          path: '/teachers/profile',
          roles: ['teacher'] as UserRole[],
        },
      ],
    },
    {
      key: '/profile',
      label: '个人中心',
      icon: <UserOutlined />,
      roles: ['admin', 'teacher', 'student'] as UserRole[],
      children: [
        {
          key: '/profile/info',
          label: '个人信息',
          path: '/profile/info',
          roles: ['admin', 'teacher', 'student'] as UserRole[],
        },
        {
          key: '/profile/password',
          label: '修改密码',
          path: '/profile/password',
          roles: ['admin', 'teacher', 'student'] as UserRole[],
        },
        {
          key: '/profile/settings',
          label: '系统设置',
          path: '/profile/settings',
          roles: ['admin', 'teacher', 'student'] as UserRole[],
        },
      ],
    },
    {
      key: '/notifications',
      label: '通知中心',
      icon: <BellOutlined />,
      roles: ['admin', 'teacher', 'student'] as UserRole[],
      children: [
        {
          key: '/notifications/list',
          label: '通知列表',
          path: '/notifications/list',
          roles: ['admin', 'teacher', 'student'] as UserRole[],
        },
      ],
    },
  ];

  // 过滤菜单项（基于用户角色）
  const filterMenuItems = (items: MenuItem[]): MenuItem[] => {
    if (!user) return [];

    return items.filter(item => {
      if (item.roles && !item.roles.includes(user.user_type)) {
        return false;
      }
      if (item.children) {
        item.children = filterMenuItems(item.children);
        return item.children.length > 0;
      }
      return true;
    });
  };

  const filteredMenuItems = filterMenuItems(menuItems);

  // 转换为 Ant Design Menu 格式
  const convertToAntdMenuItems = (items: MenuItem[]): any[] => {
    return items.map(item => ({
      key: item.key,
      icon: item.icon,
      label: item.label,
      children: item.children
        ? convertToAntdMenuItems(item.children)
        : undefined,
      onClick: item.path ? () => navigate(item.path!) : undefined,
    }));
  };

  const antdMenuItems = convertToAntdMenuItems(filteredMenuItems);

  // 用户下拉菜单
  const userMenuItems = useMemo(() => {
    if (!user) {
      return [
        {
          key: 'login',
          icon: <UserOutlined />,
          label: '请登录',
          onClick: () => navigate('/login'),
        },
      ];
    }

    return [
      {
        key: 'profile',
        icon: <UserOutlined />,
        label: '个人资料',
        onClick: () => navigate('/profile'),
      },
      {
        key: 'settings',
        icon: <SettingOutlined />,
        label: '系统设置',
        onClick: () => navigate('/settings'),
      },
      {
        type: 'divider' as const,
      },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
        onClick: () => {
          // dispatch(logout());
          navigate('/login');
        },
      },
    ];
  }, [user, navigate]);

  const unreadNotifications = notifications.filter(n => !n.read).length;

  // 获取当前主题颜色
  const themeColors = getThemeColors();

  // 动态侧边栏样式 - 根据深浅模式调整
  const siderStyle = useMemo(() => {
    // 如果主题颜色未定义，使用默认颜色
    const defaultColors = {
      primary: '#1890ff',
      secondary: '#722ed1'
    };
    
    const colors = themeColors || defaultColors;
    
    // 辅助函数：将十六进制颜色转换为RGB
    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null;
    };

    // 辅助函数：混合颜色
    const mixColors = (color1: string, color2: string, ratio: number) => {
      const rgb1 = hexToRgb(color1);
      const rgb2 = hexToRgb(color2);
      if (!rgb1 || !rgb2) return color1;

      const r = Math.round(rgb1.r * (1 - ratio) + rgb2.r * ratio);
      const g = Math.round(rgb1.g * (1 - ratio) + rgb2.g * ratio);
      const b = Math.round(rgb1.b * (1 - ratio) + rgb2.b * ratio);

      return `rgb(${r}, ${g}, ${b})`;
    };

    if (uiTheme.mode === 'dark') {
      // 深色模式：与黑色混合，创建更深的版本
      const darkPrimary = mixColors(colors.primary, '#000000', 0.4);
      const darkSecondary = mixColors(colors.secondary, '#000000', 0.4);
      return {
        background: `linear-gradient(180deg, ${darkPrimary}, ${darkSecondary})`,
      };
    } else {
      // 浅色模式：使用原始主题色
      return {
        background: `linear-gradient(180deg, ${colors.primary}, ${colors.secondary})`,
      };
    }
  }, [themeColors, uiTheme.mode]);

  return (
    <Layout className="main-layout">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={256}
        collapsedWidth={80}
        className="layout-sider"
        style={siderStyle}
      >
        <div className="logo">
          <div className="logo-icon">
            <CalendarOutlined />
          </div>
          {!collapsed && (
            <div className="logo-text">
              <div className="logo-title">课程表管理</div>
              <div className="logo-subtitle">Course Management</div>
            </div>
          )}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['/courses', '/schedules']}
          items={antdMenuItems}
          className="layout-menu"
        />
      </Sider>

      <Layout className="layout-main">
        <Header className="layout-header">
          <div className="header-left">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="trigger-btn"
            />
          </div>

          <div className="header-right">
            <Space size="middle">
              <ThemeSelector />

              <Badge count={unreadNotifications} size="small">
                <Button
                  type="text"
                  icon={<BellOutlined />}
                  onClick={() => navigate('/notifications')}
                />
              </Badge>

              {/* 头像按钮 */}
              <Dropdown
                menu={{ items: userMenuItems }}
                placement="bottomRight"
                trigger={['click']}
                disabled={!user}
              >
                <div 
                  className="user-info"
                  style={{ 
                    cursor: user ? 'pointer' : 'default', 
                    display: 'flex', 
                    alignItems: 'center',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    transition: 'background-color 0.2s',
                    userSelect: 'none',
                    opacity: user ? 1 : 0.6,
                  }}
                  onMouseEnter={(e) => {
                    if (user) {
                      e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  onClick={(e) => {
                    if (!user) {
                      e.preventDefault();
                      e.stopPropagation();
                    }
                  }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      if (!user) {
                        e.preventDefault();
                        e.stopPropagation();
                      }
                    }
                  }}
                >
                  <Avatar
                    size="small"
                    src={user?.avatar}
                    icon={<UserOutlined />}
                    alt={user?.first_name || '用户头像'}
                  />
                  <span className="user-name">
                    {user?.first_name || '用户'} {user?.last_name || ''}
                  </span>
                </div>
              </Dropdown>

              <Dropdown
                menu={{ items: userMenuItems }}
                placement="bottomRight"
                trigger={['click']}
                disabled={!user}
                onOpenChange={(open) => {
                  console.log('[MainLayout] Dropdown open state:', open, 'User:', user);
                }}
              >
                <div 
                  className="user-info"
                  style={{ 
                    cursor: user ? 'pointer' : 'default', 
                    display: 'flex', 
                    alignItems: 'center',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    transition: 'background-color 0.2s',
                    userSelect: 'none',
                    opacity: user ? 1 : 0.6,
                  }}
                  onMouseEnter={(e) => {
                    if (user) {
                      e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  onClick={(e) => {
                    console.log('[MainLayout] User info clicked, user:', user);
                    if (!user) {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('[MainLayout] No user, preventing dropdown');
                    }
                  }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      if (!user) {
                        e.preventDefault();
                        e.stopPropagation();
                      }
                    }
                  }}
                >
                  <Avatar
                    size="small"
                    src={user?.avatar}
                    icon={<UserOutlined />}
                    alt={user?.first_name || '用户头像'}
                  />
                  <span className="user-name">
                    {user?.first_name || '用户'} {user?.last_name || ''}
                  </span>
                </div>
              </Dropdown>
            </Space>
          </div>
        </Header>

        <Content className="layout-content">
          <div className="content-wrapper">
            <BreadcrumbNav />
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

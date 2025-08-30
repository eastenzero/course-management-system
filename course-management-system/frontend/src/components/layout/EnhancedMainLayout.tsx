import React, { useState, useEffect, useMemo } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, Badge, Space, Typography, Tooltip } from 'antd';
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
  BgColorsOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/index';
import type { MenuItem, UserRole } from '../../types/index';
import BreadcrumbNav from '../common/BreadcrumbNav';
import SimpleThemeSelector from '../common/SimpleThemeSelector';
import { EnhancedGlassButton, EnhancedGlassCard } from '../glass';
import { useTheme } from '../../hooks/useThemeV2';
import './EnhancedMainLayout.css';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface EnhancedMainLayoutProps {
  children: React.ReactNode;
}

const EnhancedMainLayout: React.FC<EnhancedMainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const { user } = useSelector((state: RootState) => state.auth);
  const { notifications } = useSelector((state: RootState) => state.app);
  const { uiTheme, getThemeColors } = useTheme();

  // 监听滚动事件，实现顶栏阴影增强
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 根据用户角色生成菜单
  const menuItems: MenuItem[] = useMemo(() => {
    const baseItems: MenuItem[] = [
      {
        key: '/dashboard',
        label: '仪表板',
        icon: <DashboardOutlined />,
        path: '/dashboard',
        roles: ['admin', 'teacher', 'student', 'academic_admin'],
      },
    ];

    if (user?.role === 'teacher') {
      baseItems.push(
        {
          key: '/courses',
          label: '课程管理',
          icon: <BookOutlined />,
          path: '/courses',
          roles: ['teacher'],
        },
        {
          key: '/grades',
          label: '成绩管理',
          icon: <EditOutlined />,
          path: '/grades',
          roles: ['teacher'],
        },
        {
          key: '/schedules',
          label: '课程表',
          icon: <CalendarOutlined />,
          path: '/schedules',
          roles: ['teacher'],
        }
      );
    } else if (user?.role === 'student') {
      baseItems.push(
        {
          key: '/my-courses',
          label: '我的课程',
          icon: <BookOutlined />,
          path: '/my-courses',
          roles: ['student'],
        },
        {
          key: '/my-grades',
          label: '我的成绩',
          icon: <TrophyOutlined />,
          path: '/my-grades',
          roles: ['student'],
        },
        {
          key: '/my-schedule',
          label: '我的课程表',
          icon: <CalendarOutlined />,
          path: '/my-schedule',
          roles: ['student'],
        }
      );
    } else if (user?.role === 'admin' || user?.role === 'academic_admin') {
      baseItems.push(
        {
          key: '/users',
          label: '用户管理',
          icon: <TeamOutlined />,
          path: '/users',
          roles: ['admin', 'academic_admin'],
        },
        {
          key: '/courses',
          label: '课程管理',
          icon: <BookOutlined />,
          path: '/courses',
          roles: ['admin', 'academic_admin'],
        },
        {
          key: '/analytics',
          label: '数据分析',
          icon: <BarChartOutlined />,
          path: '/analytics',
          roles: ['admin', 'academic_admin'],
        }
      );
    }

    return baseItems.filter(item => 
      !item.roles || item.roles.includes(user?.role as UserRole)
    );
  }, [user?.role]);

  // 处理菜单点击
  const handleMenuClick = (key: string) => {
    const item = menuItems.find(item => item.key === key);
    if (item?.path) {
      navigate(item.path);
    }
  };

  // 处理登出
  const handleLogout = () => {
    // 实现登出逻辑
    navigate('/login');
  };

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      label: '个人信息',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      label: '设置',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings'),
    },
    {
      key: 'theme',
      label: '主题设置',
      icon: <BgColorsOutlined />,
      onClick: () => setShowThemeSelector(true),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  // 获取当前主题颜色
  const themeColors = getThemeColors();

  return (
    <Layout className="enhanced-main-layout">
      {/* 侧边栏 */}
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        className={`enhanced-sidebar ${collapsed ? 'collapsed' : ''}`}
        width={280}
        collapsedWidth={80}
      >
        {/* Logo区域 */}
        <div className="sidebar-logo">
          <div className="logo-content">
            <div className="logo-icon" style={{ backgroundColor: themeColors?.primary }}>
              <HomeOutlined />
            </div>
            {!collapsed && (
              <div className="logo-text">
                <Text strong className="logo-title">课程管理系统</Text>
                <Text type="secondary" className="logo-subtitle">
                  {user?.role === 'teacher' ? '教师端' : 
                   user?.role === 'student' ? '学生端' : '管理端'}
                </Text>
              </div>
            )}
          </div>
        </div>

        {/* 菜单 */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          className="enhanced-menu"
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label,
            onClick: () => handleMenuClick(item.key),
          }))}
        />

        {/* 用户信息卡片 */}
        {!collapsed && (
          <div className="sidebar-user-card">
            <EnhancedGlassCard 
              size="small" 
              glassLevel="sm"
              className="user-info-card"
            >
              <Space>
                <Avatar 
                  size="small" 
                  icon={<UserOutlined />}
                  style={{ backgroundColor: themeColors?.accent }}
                />
                <div>
                  <Text strong className="user-name">{user?.username}</Text>
                  <br />
                  <Text type="secondary" className="user-role">
                    {user?.role === 'teacher' ? '教师' : 
                     user?.role === 'student' ? '学生' : '管理员'}
                  </Text>
                </div>
              </Space>
            </EnhancedGlassCard>
          </div>
        )}
      </Sider>

      {/* 主内容区 */}
      <Layout className="main-content-layout">
        {/* 顶栏 */}
        <Header className={`enhanced-header ${isScrolled ? 'scrolled' : ''}`}>
          <div className="header-left">
            <EnhancedGlassButton
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="collapse-trigger"
              glassLevel="sm"
            />
            
            {/* 搜索框 */}
            <div className="header-search">
              <EnhancedGlassButton
                type="text"
                icon={<SearchOutlined />}
                className="search-trigger"
                glassLevel="sm"
              />
            </div>
          </div>

          <div className="header-right">
            <Space size="middle">
              {/* 通知 */}
              <Tooltip title="通知">
                <Badge count={notifications?.length || 0} size="small">
                  <EnhancedGlassButton
                    type="text"
                    icon={<BellOutlined />}
                    className="notification-btn"
                    glassLevel="sm"
                  />
                </Badge>
              </Tooltip>

              {/* 主题切换 */}
              <Tooltip title="主题设置">
                <EnhancedGlassButton
                  type="text"
                  icon={<BgColorsOutlined />}
                  onClick={() => setShowThemeSelector(true)}
                  className="theme-btn"
                  glassLevel="sm"
                />
              </Tooltip>

              {/* 用户菜单 */}
              <Dropdown 
                menu={{ items: userMenuItems }}
                placement="bottomRight"
                trigger={['click']}
              >
                <div className="user-avatar-wrapper">
                  <Avatar 
                    icon={<UserOutlined />}
                    style={{ backgroundColor: themeColors?.primary }}
                  />
                  <Text className="user-name-text">{user?.username}</Text>
                </div>
              </Dropdown>
            </Space>
          </div>
        </Header>

        {/* 面包屑导航 */}
        <div className="breadcrumb-wrapper">
          <BreadcrumbNav />
        </div>

        {/* 内容区域 */}
        <Content className="enhanced-content">
          {children}
        </Content>
      </Layout>

      {/* 主题选择器弹出层 */}
      {showThemeSelector && (
        <div className="theme-selector-overlay" onClick={() => setShowThemeSelector(false)}>
          <div className="theme-selector-panel" onClick={e => e.stopPropagation()}>
            <SimpleThemeSelector onClose={() => setShowThemeSelector(false)} />
          </div>
        </div>
      )}
    </Layout>
  );
};

export default EnhancedMainLayout;

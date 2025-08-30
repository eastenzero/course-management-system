import React from 'react';
import { Breadcrumb } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import { breadcrumbConfig } from '../../router/routes';

interface BreadcrumbNavProps {
  className?: string;
}

const BreadcrumbNav: React.FC<BreadcrumbNavProps> = ({ className }) => {
  const location = useLocation();
  
  // 生成面包屑路径
  const generateBreadcrumbs = () => {
    const pathSnippets = location.pathname.split('/').filter(i => i);
    const breadcrumbItems = [];
    
    // 添加首页
    breadcrumbItems.push({
      title: (
        <Link to="/dashboard">
          <HomeOutlined />
          <span style={{ marginLeft: 4 }}>首页</span>
        </Link>
      ),
    });
    
    // 生成路径面包屑
    let currentPath = '';
    pathSnippets.forEach((snippet, index) => {
      currentPath += `/${snippet}`;
      const isLast = index === pathSnippets.length - 1;
      const title = breadcrumbConfig[currentPath] || snippet;
      
      if (isLast) {
        // 最后一个面包屑不需要链接
        breadcrumbItems.push({
          title: title,
        });
      } else {
        // 中间的面包屑添加链接
        breadcrumbItems.push({
          title: <Link to={currentPath}>{title}</Link>,
        });
      }
    });
    
    return breadcrumbItems;
  };

  // 如果在登录页面，不显示面包屑
  if (location.pathname === '/login') {
    return null;
  }

  return (
    <Breadcrumb
      className={className}
      items={generateBreadcrumbs()}
      style={{
        margin: '16px 0',
        fontSize: '14px',
      }}
    />
  );
};

export default BreadcrumbNav;

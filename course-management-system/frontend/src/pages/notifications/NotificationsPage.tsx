import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const NotificationListPage = React.lazy(() => import('./NotificationListPage'));
const NotificationDetailPage = React.lazy(() => import('./NotificationDetailPage'));

const NotificationsPage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到通知列表 */}
      <Route path="/" element={<Navigate to="list" replace />} />
      
      {/* 通知列表页 */}
      <Route path="list" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <NotificationListPage />
        </React.Suspense>
      } />
      
      {/* 通知详情页 */}
      <Route path=":id" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <NotificationDetailPage />
        </React.Suspense>
      } />
    </Routes>
  );
};

export default NotificationsPage;

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const ClassroomListPage = React.lazy(() => import('./ClassroomListPage'));
const ClassroomCreatePage = React.lazy(() => import('./ClassroomCreatePage'));
const ClassroomDetailPage = React.lazy(() => import('./ClassroomDetailPage'));

const ClassroomsPage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到教室列表 */}
      <Route path="/" element={<Navigate to="list" replace />} />
      
      {/* 教室列表页 */}
      <Route path="list" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ClassroomListPage />
        </React.Suspense>
      } />
      
      {/* 创建教室页 */}
      <Route path="create" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ClassroomCreatePage />
        </React.Suspense>
      } />
      
      {/* 教室详情页 */}
      <Route path=":id" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ClassroomDetailPage />
        </React.Suspense>
      } />
    </Routes>
  );
};

export default ClassroomsPage;

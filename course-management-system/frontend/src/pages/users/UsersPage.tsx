import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const UserListPage = React.lazy(() => import('./UserListPage'));
const UserCreatePage = React.lazy(() => import('./UserCreatePage'));
const UserDetailPage = React.lazy(() => import('./UserDetailPage'));
const UserEditPage = React.lazy(() => import('./UserEditPage'));

const UsersPage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到用户列表 */}
      <Route path="/" element={<Navigate to="list" replace />} />
      
      {/* 用户列表页 */}
      <Route path="list" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <UserListPage />
        </React.Suspense>
      } />
      
      {/* 创建用户页 */}
      <Route path="create" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <UserCreatePage />
        </React.Suspense>
      } />
      
      {/* 用户详情页 */}
      <Route path=":id" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <UserDetailPage />
        </React.Suspense>
      } />
      
      {/* 编辑用户页 */}
      <Route path=":id/edit" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <UserEditPage />
        </React.Suspense>
      } />
    </Routes>
  );
};

export default UsersPage;

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const PersonalInfoPage = React.lazy(() => import('./PersonalInfoPage'));
const PasswordChangePage = React.lazy(() => import('./PasswordChangePage'));
const SettingsPage = React.lazy(() => import('./SettingsPage'));

const ProfilePage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到个人信息 */}
      <Route path="/" element={<Navigate to="info" replace />} />
      
      {/* 个人信息页 */}
      <Route path="info" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <PersonalInfoPage />
        </React.Suspense>
      } />
      
      {/* 密码修改页 */}
      <Route path="password" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <PasswordChangePage />
        </React.Suspense>
      } />
      
      {/* 设置页 */}
      <Route path="settings" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <SettingsPage />
        </React.Suspense>
      } />
    </Routes>
  );
};

export default ProfilePage;

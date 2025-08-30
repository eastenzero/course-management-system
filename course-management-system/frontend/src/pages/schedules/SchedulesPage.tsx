import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const ScheduleViewPage = React.lazy(() => import('./ScheduleViewPage'));
const ScheduleManagePage = React.lazy(() => import('./ScheduleManagePage'));
const ConflictDetectionPage = React.lazy(() => import('./ConflictDetectionPage'));

const SchedulesPage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到课程表查看 */}
      <Route path="/" element={<Navigate to="view" replace />} />

      {/* 课程表查看页 */}
      <Route path="view" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ScheduleViewPage />
        </React.Suspense>
      } />

      {/* 排课管理页 */}
      <Route path="manage" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ScheduleManagePage />
        </React.Suspense>
      } />

      {/* 冲突检测页 */}
      <Route path="conflicts" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <ConflictDetectionPage />
        </React.Suspense>
      } />
    </Routes>
  );
};




export default SchedulesPage;

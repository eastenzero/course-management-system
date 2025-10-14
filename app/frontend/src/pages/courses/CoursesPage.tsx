import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 懒加载子页面组件
const CourseListPage = React.lazy(() => import('./CourseListPage'));
const CourseCreatePage = React.lazy(() => import('./CourseCreatePage'));
const CourseDetailPage = React.lazy(() => import('./CourseDetailPage'));
const CourseEditPage = React.lazy(() => import('./CourseEditPage'));

const CoursesPage: React.FC = () => {
  return (
    <Routes>
      {/* 默认重定向到课程列表 */}
      <Route path="/" element={<Navigate to="list" replace />} />

      {/* 课程列表页 */}
      <Route path="list" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <CourseListPage />
        </React.Suspense>
      } />

      {/* 创建课程页 */}
      <Route path="create" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <CourseCreatePage />
        </React.Suspense>
      } />

      {/* 课程详情页 */}
      <Route path=":id" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <CourseDetailPage />
        </React.Suspense>
      } />

      {/* 编辑课程页 */}
      <Route path=":id/edit" element={
        <React.Suspense fallback={<div>加载中...</div>}>
          <CourseEditPage />
        </React.Suspense>
      } />
    </Routes>
  );
};



export default CoursesPage;

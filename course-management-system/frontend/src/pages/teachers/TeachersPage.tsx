import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from '../../store/index';
import TeacherDashboard from './dashboard/TeacherDashboard';
import MyCourses from './courses/MyCourses';
import CourseStudents from './courses/CourseStudents';
import CourseSchedule from './courses/CourseSchedule';
import GradeEntry from './grades/GradeEntry';
import GradeManagement from './grades/GradeManagement';
import TeacherProfile from './profile/TeacherProfile';
import GradeAnalytics from './grades/GradeAnalytics';

const TeachersPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);

  // 确保只有教师可以访问
  if (!user || user.user_type !== 'teacher') {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        flexDirection: 'column',
        color: '#8c8c8c'
      }}>
        <h3>访问受限</h3>
        <p>此页面仅限教师访问</p>
      </div>
    );
  }

  return (
    <Routes>
      {/* 默认重定向到仪表板 */}
      <Route path="/" element={<Navigate to="dashboard" replace />} />
      
      {/* 教师仪表板 */}
      <Route path="dashboard" element={<TeacherDashboard />} />
      
      {/* 课程管理 */}
      <Route path="my-courses" element={<MyCourses />} />
      <Route path="course/:courseId/students" element={<CourseStudents />} />
      <Route path="schedule" element={<CourseSchedule />} />

      {/* 成绩管理 */}
      <Route path="grade-entry" element={<GradeEntry />} />
      <Route path="grade-management" element={<GradeManagement />} />
      <Route path="grade-analytics" element={<GradeAnalytics />} />

      {/* 个人信息 */}
      <Route path="profile" element={<TeacherProfile />} />
      
      {/* 未匹配的路由重定向到仪表板 */}
      <Route path="*" element={<Navigate to="dashboard" replace />} />
    </Routes>
  );
};

export default TeachersPage;

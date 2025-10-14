import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from '../../store/index';
import StudentDashboard from './dashboard/StudentDashboard';
import CourseSelection from './courses/CourseSelection';
import MyCourses from './courses/MyCourses';
import CourseSchedule from './courses/CourseSchedule';
import GradesList from './grades/GradesList';
import GradeDetail from './grades/GradeDetail';
import StudentProfile from './profile/StudentProfile';

const StudentsPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);

  // 确保只有学生可以访问
  if (!user || user.user_type !== 'student') {
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
        <p>此页面仅限学生访问</p>
      </div>
    );
  }

  return (
    <Routes>
      {/* 默认重定向到仪表板 */}
      <Route path="/" element={<Navigate to="dashboard" replace />} />
      
      {/* 学生仪表板 */}
      <Route path="dashboard" element={<StudentDashboard />} />
      
      {/* 选课相关 */}
      <Route path="course-selection" element={<CourseSelection />} />
      <Route path="my-courses" element={<MyCourses />} />
      <Route path="schedule" element={<CourseSchedule />} />
      
      {/* 成绩相关 */}
      <Route path="grades" element={<GradesList />} />
      <Route path="grades/:enrollmentId" element={<GradeDetail />} />
      
      {/* 个人信息 */}
      <Route path="profile" element={<StudentProfile />} />
      
      {/* 未匹配的路由重定向到仪表板 */}
      <Route path="*" element={<Navigate to="dashboard" replace />} />
    </Routes>
  );
};

export default StudentsPage;

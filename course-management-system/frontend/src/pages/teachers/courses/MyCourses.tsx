import React, { useState, useEffect } from 'react';
import { Card, Button, Empty, Spin, message, Modal, Descriptions, Tag } from 'antd';
import { PlusOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { teacherAPI, TeacherCourse } from '../../../services/teacherAPI';
import { courseAPI } from '../../../services/api';
import GlassCard from '../../../components/glass/GlassCard';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const MyCourses: React.FC = () => {
  const [courses, setCourses] = useState<TeacherCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<TeacherCourse | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getMyCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('获取课程列表失败:', error);
      
      // 禁用模拟数据回退，直接显示错误
      message.error('获取课程列表失败，请检查网络连接或联系管理员');
      setCourses([]); // 设置为空数组，显示“暂无课程”
      
      // 模拟数据回退已禁用
      /*
      const mockCourses: TeacherCourse[] = [
        {
          id: 1,
          code: 'CS101',
          name: '计算机科学导论',
          credits: 3,
          hours: 48,
          course_type: '必修',
          department: '计算机系',
          semester: '2024-2025-1',
          academic_year: '2024-2025',
          description: '介绍计算机科学的基本概念和原理',
          objectives: '掌握计算机科学基础知识',
          teachers_info: [],
          max_students: 50,
          min_students: 10,
          current_enrollment: 35,
          enrollment_statistics: { total: 35, by_status: {} },
          grade_statistics: {
            total_graded: 30,
            average_score: 85.5,
            grade_distribution: {},
            pass_rate: 95
          },
          is_active: true,
          is_published: true
        },
        {
          id: 2,
          code: 'CS201',
          name: '数据结构与算法',
          credits: 4,
          hours: 64,
          course_type: '必修',
          department: '计算机系',
          semester: '2024-2025-1',
          academic_year: '2024-2025',
          description: '学习基本数据结构和算法',
          objectives: '掌握常用数据结构和算法',
          teachers_info: [],
          max_students: 40,
          min_students: 15,
          current_enrollment: 28,
          enrollment_statistics: { total: 28, by_status: {} },
          grade_statistics: {
            total_graded: 25,
            average_score: 78.2,
            grade_distribution: {},
            pass_rate: 88
          },
          is_active: true,
          is_published: true
        }
      ];
      setCourses(mockCourses);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
      */
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = () => {
    navigate('/teacher/courses/create');
  };

  const handleEditCourse = (courseId: number) => {
    navigate(`/teacher/courses/edit/${courseId}`);
  };

  const handleDeleteCourse = async (courseId: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这门课程吗？此操作不可撤销。',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await courseAPI.deleteCourse(courseId);
          message.success('课程删除成功');
          fetchCourses();
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || '删除课程失败';
          message.error(errorMessage);
        }
      },
    });
  };

  const showCourseDetail = (course: TeacherCourse) => {
    setSelectedCourse(course);
    setDetailModalVisible(true);
  };

  const getStatusColor = (isActive: boolean, isPublished: boolean) => {
    if (!isPublished) {
      return 'orange';
    }
    return isActive ? 'green' : 'red';
  };

  const getStatusText = (isActive: boolean, isPublished: boolean) => {
    if (!isPublished) {
      return '未发布';
    }
    return isActive ? '进行中' : '已结束';
  };

  return (
    <div className="glass-page-background">
      {/* 动态背景 */}
      <DynamicBackground
        density={0.08}
        speed={0.8}
        lineMaxDist={120}
        triMaxDist={80}
      />

      <div className="glass-content" style={{ padding: '24px' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px' 
      }}>
        <h1 style={{ margin: 0, color: 'white' }}>我的课程</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreateCourse}
          size="large"
        >
          创建课程
        </Button>
      </div>

      <GlassCard>
        <div style={{ padding: '24px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '50px' }}>
              <Spin size="large" />
            </div>
          ) : courses.length === 0 ? (
            <Empty
              description="暂无课程"
              style={{ padding: '50px' }}
            />
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {courses.map((course, index) => (
                <Card
                  key={course.id}
                  style={{
                    background: `linear-gradient(135deg,
                      ${index % 3 === 0 ? 'rgba(74, 144, 226, 0.1)' :
                        index % 3 === 1 ? 'rgba(80, 200, 120, 0.1)' :
                        'rgba(255, 107, 107, 0.1)'} 0%,
                      rgba(255, 255, 255, 0.05) 100%)`,
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(10px)',
                  }}
                  bodyStyle={{ padding: '20px' }}
                >
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start' 
                  }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{ 
                        color: 'white', 
                        margin: '0 0 8px 0',
                        fontSize: '18px',
                        fontWeight: 'bold'
                      }}>
                        {course.name}
                      </h3>
                      <p style={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        margin: '0 0 12px 0',
                        fontSize: '14px'
                      }}>
                        {course.description}
                      </p>
                      <div style={{
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'center',
                        marginBottom: '12px'
                      }}>
                        <Tag color={getStatusColor(course.is_active, course.is_published)}>
                          {getStatusText(course.is_active, course.is_published)}
                        </Tag>
                        <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
                          学生数: {course.current_enrollment || 0}
                        </span>
                        <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
                          课程代码: {course.code}
                        </span>
                      </div>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      gap: '8px',
                      marginLeft: '16px'
                    }}>
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => handleEditCourse(course.id)}
                        style={{
                          color: 'white',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          fontSize: '12px'
                        }}
                      >
                        编辑
                      </Button>
                      <Button
                        type="text"
                        icon={<DeleteOutlined />}
                        onClick={() => handleDeleteCourse(course.id)}
                        style={{
                          color: 'white',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          fontSize: '12px'
                        }}
                      >
                        删除
                      </Button>
                      <Button
                        type="text"
                        icon={<EyeOutlined />}
                        onClick={() => showCourseDetail(course)}
                        style={{
                          color: 'white',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          fontSize: '12px'
                        }}
                      >
                        详情
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </GlassCard>

      <Modal
        title="课程详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={600}
      >
        {selectedCourse && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="课程名称">
              {selectedCourse.name}
            </Descriptions.Item>
            <Descriptions.Item label="课程代码">
              {selectedCourse.code}
            </Descriptions.Item>
            <Descriptions.Item label="课程描述">
              {selectedCourse.description}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={getStatusColor(selectedCourse.is_active, selectedCourse.is_published)}>
                {getStatusText(selectedCourse.is_active, selectedCourse.is_published)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="学分">
              {selectedCourse.credits}
            </Descriptions.Item>
            <Descriptions.Item label="学时">
              {selectedCourse.hours}
            </Descriptions.Item>
            <Descriptions.Item label="课程类型">
              {selectedCourse.course_type}
            </Descriptions.Item>
            <Descriptions.Item label="开课院系">
              {selectedCourse.department}
            </Descriptions.Item>
            <Descriptions.Item label="学期">
              {selectedCourse.semester}
            </Descriptions.Item>
            <Descriptions.Item label="学年">
              {selectedCourse.academic_year}
            </Descriptions.Item>
            <Descriptions.Item label="当前选课人数">
              {selectedCourse.current_enrollment}
            </Descriptions.Item>
            <Descriptions.Item label="最大选课人数">
              {selectedCourse.max_students}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
      </div>
    </div>
  );
};

export default MyCourses;

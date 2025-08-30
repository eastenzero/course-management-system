import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Select,
  Button,
  Space,
  Typography,
  Tabs,
  message,
  Spin,
  DatePicker,
  Form
} from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import GradeCharts from '../../../components/education/GradeCharts';
import { teacherAPI } from '../../../services/teacherAPI';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

interface Course {
  id: number;
  name: string;
  code: string;
  semester: string;
}

interface Student {
  id: number;
  username: string;
  name: string;
}

const GradeAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | undefined>();
  const [selectedStudent, setSelectedStudent] = useState<number | undefined>();
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [distributionData, setDistributionData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('distribution');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getMyCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('加载课程列表失败:', error);
      
      // 禁用模拟数据回退
      message.error('加载课程列表失败，请检查网络连接或联系管理员');
      setCourses([]); // 设置为空数组
      
      // 模拟数据回退已禁用
      /*
      const mockCourses: Course[] = [
        {
          id: 1,
          name: '计算机科学导论',
          code: 'CS101',
          semester: '2024-2025-1'
        },
        {
          id: 2,
          name: '数据结构与算法',
          code: 'CS201',
          semester: '2024-2025-1'
        }
      ];
      setCourses(mockCourses);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
      */
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async (courseId: number) => {
    try {
      const response = await teacherAPI.getCourseStudents(courseId);
      setStudents(response.data.map(item => ({
        id: item.student_info.id,
        username: item.student_info.username,
        name: item.student_info.name
      })));
    } catch (error) {
      console.error('加载学生列表失败:', error);
      
      // 禁用模拟数据回退
      message.error('加载学生列表失败，请检查网络连接或联系管理员');
      setStudents([]); // 设置为空数组
      
      // 模拟数据回退已禁用
      /*
      const mockStudents: Student[] = [
        {
          id: 1,
          username: '2024001',
          name: '张三'
        },
        {
          id: 2,
          username: '2024002', 
          name: '李四'
        }
      ];
      setStudents(mockStudents);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
      */
    }
  };

  const loadGradeDistribution = async (courseId: number) => {
    try {
      setLoading(true);
      const response = await teacherAPI.getCourseGradeDistribution(courseId);
      setDistributionData(response.data);
    } catch (error) {
      console.error('加载成绩分布数据失败:', error);
      // 使用模拟数据
      const mockDistributionData = {
        grades: {
          'A': 15,
          'B': 25,
          'C': 8,
          'D': 3,
          'F': 1
        },
        statistics: {
          average: 82.5,
          passRate: 96.2,
          excellentRate: 28.8
        }
      };
      setDistributionData(mockDistributionData);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const loadStudentTrend = async (studentId: number, semester?: string) => {
    try {
      setLoading(true);
      const response = await teacherAPI.getStudentGradeTrend(studentId, semester);
      setTrendData(response.data);
    } catch (error) {
      console.error('加载学生成绩趋势失败:', error);
      // 使用模拟数据
      const mockTrendData = {
        student: { id: studentId, name: '张三' },
        trends: [
          { semester: '2023-2024-1', score: 78 },
          { semester: '2023-2024-2', score: 82 },
          { semester: '2024-2025-1', score: 85 }
        ],
        average: 81.7
      };
      setTrendData(mockTrendData);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const loadClassComparison = async (className: string, semester: string) => {
    try {
      setLoading(true);
      const response = await teacherAPI.getClassGradeComparison(className, semester);
      setComparisonData(response.data);
    } catch (error) {
      console.error('加载班级对比数据失败:', error);
      // 使用模拟数据
      const mockComparisonData = {
        classes: [
          { name: '计算机科学1班', average: 82.5, passRate: 96.2 },
          { name: '计算机科学2班', average: 80.1, passRate: 94.5 },
          { name: '软件工程1班', average: 84.3, passRate: 97.8 }
        ],
        overall: {
          average: 82.3,
          passRate: 96.2
        }
      };
      setComparisonData(mockComparisonData);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const handleCourseChange = (courseId: number) => {
    setSelectedCourse(courseId);
    loadStudents(courseId);
    if (activeTab === 'distribution') {
      loadGradeDistribution(courseId);
    }
  };

  const handleStudentChange = (studentId: number) => {
    setSelectedStudent(studentId);
    if (activeTab === 'trend') {
      loadStudentTrend(studentId, selectedSemester);
    }
  };

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    
    // 根据切换的标签页加载相应数据
    switch (key) {
      case 'distribution':
        if (selectedCourse) {
          loadGradeDistribution(selectedCourse);
        }
        break;
      case 'trend':
        if (selectedStudent) {
          loadStudentTrend(selectedStudent, selectedSemester);
        }
        break;
      case 'comparison':
        if (selectedClass && selectedSemester) {
          loadClassComparison(selectedClass, selectedSemester);
        }
        break;
    }
  };

  const exportData = async () => {
    try {
      let exportUrl = '';
      let filename = '';
      
      switch (activeTab) {
        case 'distribution':
          if (!selectedCourse) {
            message.warning('请先选择课程');
            return;
          }
          exportUrl = `/api/courses/${selectedCourse}/grades/export/`;
          filename = `课程成绩分布-${Date.now()}.xlsx`;
          break;
        case 'trend':
          if (!selectedStudent) {
            message.warning('请先选择学生');
            return;
          }
          // 实现学生成绩趋势导出
          message.info('学生成绩趋势导出功能开发中');
          return;
        case 'comparison':
          if (!selectedClass || !selectedSemester) {
            message.warning('请先选择班级和学期');
            return;
          }
          // 实现班级对比导出
          message.info('班级对比导出功能开发中');
          return;
      }

      // 创建下载链接
      const link = document.createElement('a');
      link.href = exportUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const refreshData = () => {
    switch (activeTab) {
      case 'distribution':
        if (selectedCourse) {
          loadGradeDistribution(selectedCourse);
        }
        break;
      case 'trend':
        if (selectedStudent) {
          loadStudentTrend(selectedStudent, selectedSemester);
        }
        break;
      case 'comparison':
        if (selectedClass && selectedSemester) {
          loadClassComparison(selectedClass, selectedSemester);
        }
        break;
    }
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
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Title level={2}>成绩分析</Title>
            <Text type="secondary">查看和分析学生成绩数据</Text>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={refreshData}
                loading={loading}
              >
                刷新
              </Button>
              <Button 
                type="primary" 
                icon={<DownloadOutlined />}
                onClick={exportData}
              >
                导出数据
              </Button>
            </Space>
          </Col>
        </Row>

        <Tabs activeKey={activeTab} onChange={handleTabChange}>
          <TabPane 
            tab={
              <span>
                <PieChartOutlined />
                成绩分布
              </span>
            } 
            key="distribution"
          >
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col span={8}>
                <Select
                  placeholder="选择课程"
                  style={{ width: '100%' }}
                  value={selectedCourse}
                  onChange={handleCourseChange}
                  loading={loading}
                >
                  {courses.map(course => (
                    <Option key={course.id} value={course.id}>
                      {course.name} ({course.code})
                    </Option>
                  ))}
                </Select>
              </Col>
            </Row>
            
            <GradeCharts
              type="distribution"
              data={distributionData}
              loading={loading}
              courseId={selectedCourse}
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <LineChartOutlined />
                成绩趋势
              </span>
            } 
            key="trend"
          >
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col span={6}>
                <Select
                  placeholder="选择课程"
                  style={{ width: '100%' }}
                  value={selectedCourse}
                  onChange={handleCourseChange}
                  loading={loading}
                >
                  {courses.map(course => (
                    <Option key={course.id} value={course.id}>
                      {course.name} ({course.code})
                    </Option>
                  ))}
                </Select>
              </Col>
              <Col span={6}>
                <Select
                  placeholder="选择学生"
                  style={{ width: '100%' }}
                  value={selectedStudent}
                  onChange={handleStudentChange}
                  disabled={!selectedCourse}
                >
                  {students.map(student => (
                    <Option key={student.id} value={student.id}>
                      {student.name} ({student.username})
                    </Option>
                  ))}
                </Select>
              </Col>
              <Col span={6}>
                <Select
                  placeholder="选择学期"
                  style={{ width: '100%' }}
                  value={selectedSemester}
                  onChange={setSelectedSemester}
                  allowClear
                >
                  <Option value="2024-2025-1">2024-2025-1</Option>
                  <Option value="2024-2025-2">2024-2025-2</Option>
                  <Option value="2023-2024-1">2023-2024-1</Option>
                  <Option value="2023-2024-2">2023-2024-2</Option>
                </Select>
              </Col>
            </Row>
            
            <GradeCharts
              type="trend"
              data={trendData}
              loading={loading}
              studentId={selectedStudent}
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BarChartOutlined />
                班级对比
              </span>
            } 
            key="comparison"
          >
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col span={8}>
                <Select
                  placeholder="选择班级"
                  style={{ width: '100%' }}
                  value={selectedClass}
                  onChange={setSelectedClass}
                >
                  <Option value="计算机科学1班">计算机科学1班</Option>
                  <Option value="计算机科学2班">计算机科学2班</Option>
                  <Option value="软件工程1班">软件工程1班</Option>
                  <Option value="软件工程2班">软件工程2班</Option>
                </Select>
              </Col>
              <Col span={8}>
                <Select
                  placeholder="选择学期"
                  style={{ width: '100%' }}
                  value={selectedSemester}
                  onChange={setSelectedSemester}
                >
                  <Option value="2024-2025-1">2024-2025-1</Option>
                  <Option value="2024-2025-2">2024-2025-2</Option>
                  <Option value="2023-2024-1">2023-2024-1</Option>
                  <Option value="2023-2024-2">2023-2024-2</Option>
                </Select>
              </Col>
            </Row>
            
            <GradeCharts
              type="comparison"
              data={comparisonData}
              loading={loading}
            />
          </TabPane>
        </Tabs>
      </Card>
      </div>
    </div>
  );
};

export default GradeAnalytics;

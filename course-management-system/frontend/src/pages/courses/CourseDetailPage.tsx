import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Space,
  Descriptions,
  Tag,
  Tabs,
  Table,
  message,
  Spin,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  UserOutlined,
  BookOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { courseAPI } from '../../services/api';

const { Title } = Typography;
const { TabPane } = Tabs;

interface Course {
  id: number;
  name: string;
  code: string;
  credits: number;
  department: string;
  course_type: string;
  course_type_display: string;
  max_students: number;
  current_enrollment: number;
  hours: number;
  semester: string;
  academic_year: string;
  is_active: boolean;
  is_published: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface Student {
  id: string;
  name: string;
  studentId: string;
  department: string;
  enrollDate: string;
}

const CourseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourseDetail = async () => {
      try {
        setLoading(true);

        if (!id) {
          message.error('课程ID不存在');
          navigate('/courses/list');
          return;
        }

        const response = await courseAPI.getCourse(parseInt(id));
        setCourse(response.data);

        // 暂时使用模拟学生数据，后续可以通过API获取
        const mockStudents: Student[] = [];
        setStudents(mockStudents);
      } catch (error) {
        console.error('获取课程详情失败:', error);
        message.error('获取课程详情失败');
        navigate('/courses/list');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCourseDetail();
    }
  }, [id]);

  const studentColumns = [
    {
      title: '学号',
      dataIndex: 'studentId',
      key: 'studentId',
      width: 120,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
    },
    {
      title: '选课时间',
      dataIndex: 'enrollDate',
      key: 'enrollDate',
      width: 120,
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ minHeight: '200px' }} />
        </Spin>
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>课程不存在</Title>
        <Button onClick={() => navigate('/courses/list')}>
          返回课程列表
        </Button>
      </div>
    );
  }

  return (
    <div className="course-detail-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/courses/list')}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>{course.name}</Title>
          <Tag color={course.is_active ? 'green' : 'red'}>
            {course.is_active ? '活跃' : '非活跃'}
          </Tag>
          <Tag color={course.is_published ? 'blue' : 'orange'}>
            {course.is_published ? '已发布' : '未发布'}
          </Tag>
        </Space>
        <Space>
          <Button 
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/courses/${id}/edit`)}
          >
            编辑课程
          </Button>
        </Space>
      </div>

      <Card>
        <Tabs defaultActiveKey="basic">
          <TabPane 
            tab={
              <span>
                <BookOutlined />
                基本信息
              </span>
            } 
            key="basic"
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="课程代码">{course.code}</Descriptions.Item>
              <Descriptions.Item label="课程名称">{course.name}</Descriptions.Item>
              <Descriptions.Item label="学分">{course.credits}</Descriptions.Item>
              <Descriptions.Item label="院系">{course.department}</Descriptions.Item>
              <Descriptions.Item label="课程类型">{course.course_type_display}</Descriptions.Item>
              <Descriptions.Item label="总学时">{course.hours}学时</Descriptions.Item>
              <Descriptions.Item label="最大学生数">{course.max_students}人</Descriptions.Item>
              <Descriptions.Item label="当前选课人数">{course.current_enrollment}人</Descriptions.Item>
              <Descriptions.Item label="学期">{course.semester}</Descriptions.Item>
              <Descriptions.Item label="学年">{course.academic_year}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Space>
                  <Tag color={course.is_active ? 'green' : 'red'}>
                    {course.is_active ? '活跃' : '非活跃'}
                  </Tag>
                  <Tag color={course.is_published ? 'blue' : 'orange'}>
                    {course.is_published ? '已发布' : '未发布'}
                  </Tag>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">{new Date(course.created_at).toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="课程描述" span={2}>
                {course.description || '暂无描述'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <UserOutlined />
                选课学生 ({students.length})
              </span>
            } 
            key="students"
          >
            <Table
              columns={studentColumns}
              dataSource={students}
              rowKey="id"
              pagination={{
                total: students.length,
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 名学生`,
              }}
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BarChartOutlined />
                统计信息
              </span>
            } 
            key="statistics"
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="选课率">
                {((course.enrolled / course.capacity) * 100).toFixed(1)}%
              </Descriptions.Item>
              <Descriptions.Item label="剩余名额">
                {course.capacity - course.enrolled}人
              </Descriptions.Item>
              <Descriptions.Item label="选课状态">
                {course.enrolled >= course.capacity ? '已满' : '可选'}
              </Descriptions.Item>
              <Descriptions.Item label="课程热度">
                {course.enrolled > course.capacity * 0.8 ? '热门' : '一般'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default CourseDetailPage;

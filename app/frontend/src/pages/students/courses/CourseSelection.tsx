import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  message,
  Descriptions,
  Progress,
  Alert,
  Tooltip,
  Typography,
  Row,
  Col,
  Spin
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  UserOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { studentAPI } from '../../../services/studentAPI';

const { Option } = Select;
const { Text, Title } = Typography;
const { confirm } = Modal;

interface Course {
  id: number;
  code: string;
  name: string;
  credits: number;
  hours: number;
  course_type: string;
  department: string;
  semester: string;
  description: string;
  teachers_info: any[];
  max_students: number;
  current_enrollment: number;
  enrollment_info: {
    current: number;
    max: number;
    available: number;
    is_full: boolean;
  };
  can_enroll: boolean;
  conflict_info: any[];
}

const CourseSelection: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [enrolling, setEnrolling] = useState(false);
  
  // 筛选条件
  const [filters, setFilters] = useState({
    search: '',
    semester: '',
    department: '',
    course_type: ''
  });

  useEffect(() => {
    fetchAvailableCourses();
  }, [filters]);

  const fetchAvailableCourses = async () => {
    try {
      setLoading(true);
      const params = Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      );
      const response = await studentAPI.getAvailableCourses(params);
      setCourses(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取可选课程失败');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrollCourse = async (courseId: number) => {
    try {
      setEnrolling(true);
      await studentAPI.enrollCourse(courseId);
      message.success('选课成功！');
      fetchAvailableCourses(); // 刷新课程列表
    } catch (error: any) {
      message.error(error.response?.data?.error || '选课失败');
    } finally {
      setEnrolling(false);
    }
  };

  const showEnrollConfirm = (course: Course) => {
    confirm({
      title: '确认选课',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>您确定要选择以下课程吗？</p>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="课程名称">{course.name}</Descriptions.Item>
            <Descriptions.Item label="课程代码">{course.code}</Descriptions.Item>
            <Descriptions.Item label="学分">{course.credits}</Descriptions.Item>
            <Descriptions.Item label="授课教师">
              {course.teachers_info.map(t => t.name).join(', ')}
            </Descriptions.Item>
          </Descriptions>
        </div>
      ),
      onOk: () => handleEnrollCourse(course.id),
      okText: '确认选课',
      cancelText: '取消',
    });
  };

  const showCourseDetail = (course: Course) => {
    setSelectedCourse(course);
    setDetailModalVisible(true);
  };

  const columns: ColumnsType<Course> = [
    {
      title: '课程信息',
      key: 'course_info',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {record.name}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {record.code} | {record.credits}学分 | {record.hours}学时
          </div>
        </div>
      ),
    },
    {
      title: '课程类型',
      dataIndex: 'course_type',
      key: 'course_type',
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          'required': 'red',
          'elective': 'blue',
          'public': 'green',
          'professional': 'orange'
        };
        return <Tag color={colorMap[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '开课院系',
      dataIndex: 'department',
      key: 'department',
    },
    {
      title: '授课教师',
      key: 'teachers',
      render: (_, record) => (
        <div>
          {record.teachers_info.map((teacher, index) => (
            <div key={index} style={{ fontSize: '12px' }}>
              <UserOutlined /> {teacher.name}
            </div>
          ))}
        </div>
      ),
    },
    {
      title: '选课情况',
      key: 'enrollment',
      render: (_, record) => {
        const { current, max, is_full } = record.enrollment_info;
        const percentage = (current / max) * 100;
        
        return (
          <div style={{ width: '120px' }}>
            <Progress
              percent={percentage}
              size="small"
              status={is_full ? 'exception' : 'active'}
              format={() => `${current}/${max}`}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
              {is_full ? '已满员' : `剩余${max - current}个名额`}
            </div>
          </div>
        );
      },
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            onClick={() => showCourseDetail(record)}
          >
            详情
          </Button>
          <Button
            type="primary"
            size="small"
            disabled={!record.can_enroll || record.enrollment_info.is_full}
            loading={enrolling}
            onClick={() => showEnrollConfirm(record)}
            icon={<CheckCircleOutlined />}
          >
            {record.enrollment_info.is_full ? '已满员' : '选课'}
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>选课系统</Title>
      
      {/* 筛选条件 */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="搜索课程名称或代码"
              prefix={<SearchOutlined />}
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择学期"
              style={{ width: '100%' }}
              value={filters.semester}
              onChange={(value) => setFilters({ ...filters, semester: value })}
              allowClear
            >
              <Option value="2024-2025-1">2024-2025学年第一学期</Option>
              <Option value="2024-2025-2">2024-2025学年第二学期</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择院系"
              style={{ width: '100%' }}
              value={filters.department}
              onChange={(value) => setFilters({ ...filters, department: value })}
              allowClear
            >
              <Option value="计算机学院">计算机学院</Option>
              <Option value="数学学院">数学学院</Option>
              <Option value="物理学院">物理学院</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="课程类型"
              style={{ width: '100%' }}
              value={filters.course_type}
              onChange={(value) => setFilters({ ...filters, course_type: value })}
              allowClear
            >
              <Option value="required">必修课</Option>
              <Option value="elective">选修课</Option>
              <Option value="public">公共课</Option>
              <Option value="professional">专业课</Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 选课提示 */}
      <Alert
        message="选课提示"
        description="请仔细查看课程信息，确认无时间冲突后再进行选课。选课成功后可在我的课程中查看。"
        type="info"
        showIcon
        style={{ marginBottom: '16px' }}
      />

      {/* 课程列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={courses}
          rowKey="id"
          loading={loading}
          pagination={{
            total: courses.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 门课程`,
          }}
        />
      </Card>

      {/* 课程详情模态框 */}
      <Modal
        title="课程详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedCourse && selectedCourse.can_enroll && !selectedCourse.enrollment_info.is_full && (
            <Button
              key="enroll"
              type="primary"
              loading={enrolling}
              onClick={() => {
                setDetailModalVisible(false);
                showEnrollConfirm(selectedCourse);
              }}
            >
              选择此课程
            </Button>
          ),
        ]}
        width={800}
      >
        {selectedCourse && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="课程名称" span={2}>
              {selectedCourse.name}
            </Descriptions.Item>
            <Descriptions.Item label="课程代码">
              {selectedCourse.code}
            </Descriptions.Item>
            <Descriptions.Item label="学分">
              {selectedCourse.credits}
            </Descriptions.Item>
            <Descriptions.Item label="学时">
              {selectedCourse.hours}
            </Descriptions.Item>
            <Descriptions.Item label="课程类型">
              <Tag>{selectedCourse.course_type}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="开课院系">
              {selectedCourse.department}
            </Descriptions.Item>
            <Descriptions.Item label="开课学期">
              {selectedCourse.semester}
            </Descriptions.Item>
            <Descriptions.Item label="授课教师" span={2}>
              {selectedCourse.teachers_info.map(teacher => teacher.name).join(', ')}
            </Descriptions.Item>
            <Descriptions.Item label="选课情况" span={2}>
              <Progress
                percent={(selectedCourse.enrollment_info.current / selectedCourse.enrollment_info.max) * 100}
                format={() => `${selectedCourse.enrollment_info.current}/${selectedCourse.enrollment_info.max}`}
              />
            </Descriptions.Item>
            <Descriptions.Item label="课程描述" span={2}>
              {selectedCourse.description || '暂无描述'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default CourseSelection;

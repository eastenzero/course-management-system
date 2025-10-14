import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Input,
  Select,
  Button,
  Space,
  Typography,
  Tag,
  Avatar,
  Progress,
  message,
  Row,
  Col,
  Statistic,
  Spin
} from 'antd';
import {
  SearchOutlined,
  UserOutlined,
  MailOutlined,
  ArrowLeftOutlined,
  ExportOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useParams, useNavigate } from 'react-router-dom';
import { teacherAPI } from '../../../services/teacherAPI';
import type { CourseStudent } from '../../../services/teacherAPI';

const { Option } = Select;
const { Title, Text } = Typography;

const CourseStudents: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [students, setStudents] = useState<CourseStudent[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<CourseStudent[]>([]);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    if (courseId) {
      fetchStudents();
    }
  }, [courseId]);

  useEffect(() => {
    filterStudents();
  }, [students, searchText, statusFilter]);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getCourseStudents(parseInt(courseId!), {
        status: statusFilter || undefined,
        search: searchText || undefined
      });
      setStudents(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取学生列表失败');
    } finally {
      setLoading(false);
    }
  };

  const filterStudents = () => {
    let filtered = [...students];

    if (searchText) {
      filtered = filtered.filter(student =>
        student.student_info.name.toLowerCase().includes(searchText.toLowerCase()) ||
        student.student_info.student_id.includes(searchText) ||
        student.student_info.username.toLowerCase().includes(searchText.toLowerCase())
      );
    }

    if (statusFilter) {
      filtered = filtered.filter(student => student.enrollment_info.status === statusFilter);
    }

    setFilteredStudents(filtered);
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      'enrolled': 'blue',
      'completed': 'green',
      'dropped': 'red',
      'failed': 'red'
    };
    return colorMap[status] || 'default';
  };

  const getGradeColor = (score: number | null) => {
    if (score === null) return '#666';
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const columns: ColumnsType<CourseStudent> = [
    {
      title: '学生信息',
      key: 'student',
      render: (_, record) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Avatar icon={<UserOutlined />} style={{ marginRight: '12px' }} />
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              {record.student_info.name}
            </div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              学号：{record.student_info.student_id}
            </div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              用户名：{record.student_info.username}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: '专业班级',
      key: 'major',
      render: (_, record) => (
        <div>
          <div style={{ marginBottom: '4px' }}>
            {record.student_info.major}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {record.student_info.class_name}
          </div>
        </div>
      ),
    },
    {
      title: '联系方式',
      key: 'contact',
      render: (_, record) => (
        <div>
          <div style={{ marginBottom: '4px', fontSize: '12px' }}>
            <MailOutlined /> {record.student_info.email}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            院系：{record.student_info.department}
          </div>
        </div>
      ),
    },
    {
      title: '选课状态',
      key: 'status',
      render: (_, record) => (
        <div>
          <Tag color={getStatusColor(record.enrollment_info.status)}>
            {record.enrollment_info.status_display}
          </Tag>
          <div style={{ color: '#666', fontSize: '12px', marginTop: '4px' }}>
            选课时间：{new Date(record.enrollment_info.enrolled_at).toLocaleDateString()}
          </div>
        </div>
      ),
    },
    {
      title: '学习进度',
      key: 'progress',
      render: (_, record) => (
        <div style={{ width: '120px' }}>
          <div style={{ marginBottom: '4px' }}>
            <Text style={{ fontSize: '12px' }}>出勤率</Text>
            <Progress
              percent={record.progress_info.attendance_rate}
              size="small"
              format={() => `${record.progress_info.attendance_rate}%`}
            />
          </div>
          <div>
            <Text style={{ fontSize: '12px' }}>作业完成</Text>
            <Progress
              percent={record.progress_info.assignment_completion}
              size="small"
              format={() => `${record.progress_info.assignment_completion}%`}
            />
          </div>
        </div>
      ),
    },
    {
      title: '成绩',
      key: 'grade',
      render: (_, record) => (
        <div style={{ textAlign: 'center' }}>
          {record.score !== null ? (
            <>
              <div style={{ 
                fontSize: '16px', 
                fontWeight: 'bold', 
                color: getGradeColor(record.score),
                marginBottom: '4px'
              }}>
                {record.score}
              </div>
              <Tag color={getGradeColor(record.score)}>
                {record.grade}
              </Tag>
            </>
          ) : (
            <Text type="secondary">未录入</Text>
          )}
        </div>
      ),
      sorter: (a, b) => (a.score || 0) - (b.score || 0),
    },
  ];

  // 统计数据
  const statistics = {
    total: filteredStudents.length,
    enrolled: filteredStudents.filter(s => s.enrollment_info.status === 'enrolled').length,
    completed: filteredStudents.filter(s => s.enrollment_info.status === 'completed').length,
    graded: filteredStudents.filter(s => s.score !== null).length,
    averageScore: filteredStudents.filter(s => s.score !== null).length > 0
      ? filteredStudents.filter(s => s.score !== null).reduce((sum, s) => sum + (s.score || 0), 0) / filteredStudents.filter(s => s.score !== null).length
      : 0
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/teachers/my-courses')}
          style={{ marginBottom: '16px' }}
        >
          返回课程列表
        </Button>
        <Title level={2}>学生管理</Title>
      </div>

      {/* 统计概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="学生总数"
              value={statistics.total}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="在读学生"
              value={statistics.enrolled}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已评分"
              value={statistics.graded}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均成绩"
              value={statistics.averageScore}
              precision={1}
              suffix="分"
              valueStyle={{ color: getGradeColor(statistics.averageScore) }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选条件 */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Input
              placeholder="搜索学生姓名、学号或用户名"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Select
              placeholder="选择状态"
              style={{ width: '100%' }}
              value={statusFilter}
              onChange={setStatusFilter}
              allowClear
            >
              <Option value="enrolled">在读</Option>
              <Option value="completed">已完成</Option>
              <Option value="dropped">已退课</Option>
              <Option value="failed">未通过</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Space>
              <Button
                icon={<ExportOutlined />}
                onClick={() => message.info('导出功能开发中...')}
              >
                导出名单
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 学生列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredStudents}
          rowKey="id"
          loading={loading}
          pagination={{
            total: filteredStudents.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 名学生`,
          }}
        />
      </Card>
    </div>
  );
};

export default CourseStudents;

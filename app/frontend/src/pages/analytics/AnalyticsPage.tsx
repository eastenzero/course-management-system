import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Select,
  DatePicker,
  Space,
  Tag,
  Spin,
  message,
} from 'antd';
import {
  BookOutlined,
  UserOutlined,
  TeamOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  HomeOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { LineChart, BarChart, PieChart } from '../../components/charts';
import { useRequest } from '../../hooks/useApi';

const { Title } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface DashboardStats {
  total_users: number;
  total_students: number;
  total_teachers: number;
  total_courses: number;
  total_enrollments: number;
  total_classrooms: number;
  total_schedules: number;
  user_growth_rate: number;
  course_growth_rate: number;
  enrollment_growth_rate: number;
}

interface CourseAnalytics {
  course_id: number;
  course_name: string;
  course_code: string;
  enrollment_count: number;
  max_students: number;
  enrollment_rate: number;
  department: string;
  course_type: string;
  credits: number;
}

interface UserAnalytics {
  user_type: string;
  count: number;
  percentage: number;
  active_count: number;
  active_rate: number;
}

interface OverviewData {
  dashboard_stats: DashboardStats;
  course_type_distribution: Array<{
    course_type: string;
    count: number;
    percentage: number;
  }>;
  department_stats: Array<{
    department: string;
    course_count: number;
    student_count: number;
    enrollment_count: number;
  }>;
  top_courses: CourseAnalytics[];
}

const AnalyticsPage: React.FC = () => {
  const [selectedSemester, setSelectedSemester] = useState('2024-1');
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [courseAnalytics, setCourseAnalytics] = useState<CourseAnalytics[]>([]);
  const [userAnalytics, setUserAnalytics] = useState<UserAnalytics[]>([]);
  const [loading, setLoading] = useState(true);

  const { request } = useRequest();

  // 获取分析数据
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);

        // 并行获取所有分析数据
        const [overviewRes, courseRes, userRes] = await Promise.all([
          request('/analytics/overview/'),
          request('/analytics/courses/'),
          request('/analytics/users/'),
        ]);

        if (overviewRes.code === 200) {
          setOverviewData(overviewRes.data);
        }

        if (courseRes.code === 200) {
          setCourseAnalytics(courseRes.data);
        }

        if (userRes.code === 200) {
          setUserAnalytics(userRes.data);
        }

      } catch (error) {
        console.error('获取分析数据失败:', error);
        message.error('获取分析数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [selectedSemester]);

  const courseColumns = [
    {
      title: '课程名称',
      dataIndex: 'course_name',
      key: 'course_name',
      width: 200,
    },
    {
      title: '课程代码',
      dataIndex: 'course_code',
      key: 'course_code',
      width: 120,
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
      render: (dept: string) => dept || '未分配',
    },
    {
      title: '选课人数',
      key: 'enrollment',
      width: 120,
      render: (record: CourseAnalytics) => `${record.enrollment_count}/${record.max_students}`,
    },
    {
      title: '选课率',
      dataIndex: 'enrollment_rate',
      key: 'enrollment_rate',
      width: 120,
      render: (rate: number) => (
        <div>
          <Progress
            percent={rate}
            size="small"
            status={rate > 80 ? 'success' : rate > 60 ? 'normal' : 'exception'}
          />
          <span style={{ fontSize: '12px' }}>{rate.toFixed(1)}%</span>
        </div>
      ),
    },
    {
      title: '学分',
      dataIndex: 'credits',
      key: 'credits',
      width: 80,
    },
    {
      title: '课程类型',
      dataIndex: 'course_type',
      key: 'course_type',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          'required': { text: '必修', color: 'red' },
          'elective': { text: '选修', color: 'blue' },
          'public': { text: '公共', color: 'green' },
          'professional': { text: '专业', color: 'orange' },
        };
        const typeInfo = typeMap[type] || { text: type, color: 'default' };
        return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>;
      },
    },
  ];

  const userColumns = [
    {
      title: '用户类型',
      dataIndex: 'user_type',
      key: 'user_type',
      width: 120,
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          'admin': { text: '管理员', color: 'red' },
          'teacher': { text: '教师', color: 'blue' },
          'student': { text: '学生', color: 'green' },
          'academic_admin': { text: '教务管理员', color: 'orange' },
        };
        const typeInfo = typeMap[type] || { text: type, color: 'default' };
        return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>;
      },
    },
    {
      title: '用户数量',
      dataIndex: 'count',
      key: 'count',
      width: 100,
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      width: 100,
      render: (percentage: number) => `${percentage.toFixed(1)}%`,
    },
    {
      title: '活跃用户',
      dataIndex: 'active_count',
      key: 'active_count',
      width: 100,
    },
    {
      title: '活跃率',
      dataIndex: 'active_rate',
      key: 'active_rate',
      width: 100,
      render: (rate: number) => (
        <Progress
          percent={rate}
          size="small"
          format={(percent) => `${percent?.toFixed(1)}%`}
          status={rate > 90 ? 'success' : rate > 70 ? 'normal' : 'exception'}
        />
      ),
    },
  ];

  // 准备图表数据
  const courseTypeChartData = overviewData?.course_type_distribution.map(item => ({
    name: item.course_type === 'elective' ? '选修' :
          item.course_type === 'required' ? '必修' :
          item.course_type === 'public' ? '公共' : '专业',
    value: item.count,
  })) || [];

  const userTypeChartData = userAnalytics.map(item => ({
    name: item.user_type === 'student' ? '学生' :
          item.user_type === 'teacher' ? '教师' :
          item.user_type === 'admin' ? '管理员' : '教务管理员',
    value: item.count,
  }));

  const topCoursesChartData = overviewData?.top_courses.slice(0, 10).map(course => ({
    name: course.course_name,
    value: course.enrollment_count,
  })) || [];

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px'
      }}>
        <Spin size="large" tip="加载分析数据中..." />
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="page-header">
        <Title level={2}>
          <BarChartOutlined style={{ marginRight: 8 }} />
          数据分析
        </Title>
        <p>统计报表和可视化图表</p>
      </div>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 筛选器 */}
        <Card>
          <Row gutter={16}>
            <Col xs={24} sm={12} md={8}>
              <Select
                value={selectedSemester}
                onChange={setSelectedSemester}
                style={{ width: '100%' }}
              >
                <Option value="2024-1">2024年春季学期</Option>
                <Option value="2024-2">2024年秋季学期</Option>
                <Option value="2025-1">2025年春季学期</Option>
              </Select>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <RangePicker style={{ width: '100%' }} />
            </Col>
          </Row>
        </Card>

        {/* 总体统计 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={overviewData?.dashboard_stats.total_users || 0}
                prefix={<TeamOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总课程数"
                value={overviewData?.dashboard_stats.total_courses || 0}
                prefix={<BookOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总选课数"
                value={overviewData?.dashboard_stats.total_enrollments || 0}
                prefix={<UserOutlined style={{ color: '#faad14' }} />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总教室数"
                value={overviewData?.dashboard_stats.total_classrooms || 0}
                prefix={<HomeOutlined style={{ color: '#722ed1' }} />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 增长率统计 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="用户增长率"
                value={overviewData?.dashboard_stats.user_growth_rate || 0}
                precision={1}
                suffix="%"
                prefix={
                  (overviewData?.dashboard_stats.user_growth_rate || 0) > 0 ?
                    <RiseOutlined style={{ color: '#52c41a' }} /> :
                    <FallOutlined style={{ color: '#ff4d4f' }} />
                }
                valueStyle={{
                  color: (overviewData?.dashboard_stats.user_growth_rate || 0) > 0 ? '#52c41a' : '#ff4d4f'
                }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="课程增长率"
                value={overviewData?.dashboard_stats.course_growth_rate || 0}
                precision={1}
                suffix="%"
                prefix={
                  (overviewData?.dashboard_stats.course_growth_rate || 0) > 0 ?
                    <RiseOutlined style={{ color: '#52c41a' }} /> :
                    <FallOutlined style={{ color: '#ff4d4f' }} />
                }
                valueStyle={{
                  color: (overviewData?.dashboard_stats.course_growth_rate || 0) > 0 ? '#52c41a' : '#ff4d4f'
                }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="选课增长率"
                value={overviewData?.dashboard_stats.enrollment_growth_rate || 0}
                precision={1}
                suffix="%"
                prefix={
                  (overviewData?.dashboard_stats.enrollment_growth_rate || 0) > 0 ?
                    <RiseOutlined style={{ color: '#52c41a' }} /> :
                    <FallOutlined style={{ color: '#ff4d4f' }} />
                }
                valueStyle={{
                  color: (overviewData?.dashboard_stats.enrollment_growth_rate || 0) > 0 ? '#52c41a' : '#ff4d4f'
                }}
              />
            </Card>
          </Col>
        </Row>

        {/* 图表展示 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="课程类型分布">
              <PieChart
                data={courseTypeChartData}
                height={300}
                showLegend={true}
                showLabel={true}
                showPercentage={true}
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="用户类型分布">
              <PieChart
                data={userTypeChartData}
                height={300}
                showLegend={true}
                showLabel={true}
                showPercentage={true}
                roseType={true}
              />
            </Card>
          </Col>
        </Row>

        {/* 热门课程图表 */}
        <Card title="热门课程排行">
          <BarChart
            data={topCoursesChartData}
            height={400}
            horizontal={true}
            showLabel={true}
            title="选课人数最多的课程"
          />
        </Card>

        {/* 课程统计表 */}
        <Card title="课程分析详情">
          <Table
            columns={courseColumns}
            dataSource={courseAnalytics}
            rowKey="course_id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 门课程`,
            }}
          />
        </Card>

        {/* 用户统计表 */}
        <Card title="用户分析概览">
          <Table
            columns={userColumns}
            dataSource={userAnalytics}
            rowKey="user_type"
            pagination={false}
          />
        </Card>

        {/* 院系统计 */}
        {overviewData?.department_stats && overviewData.department_stats.length > 0 && (
          <Card title="院系统计分析">
            <BarChart
              data={overviewData.department_stats.map(dept => ({
                name: dept.department || '未分配',
                value: dept.course_count,
              }))}
              height={300}
              title="各院系课程数量"
              showLabel={true}
            />
          </Card>
        )}

        {/* 系统概览 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="系统活跃度">
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ marginBottom: '16px' }}>
                  <Progress
                    type="circle"
                    percent={85}
                    format={(percent) => `${percent}%`}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                </div>
                <p style={{ color: '#8c8c8c' }}>系统整体活跃度</p>
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="数据完整性">
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ marginBottom: '16px' }}>
                  <Progress
                    type="circle"
                    percent={92}
                    format={(percent) => `${percent}%`}
                    strokeColor={{
                      '0%': '#faad14',
                      '100%': '#52c41a',
                    }}
                  />
                </div>
                <p style={{ color: '#8c8c8c' }}>数据完整性评分</p>
              </div>
            </Card>
          </Col>
        </Row>
      </Space>
    </div>
  );
};

export default AnalyticsPage;

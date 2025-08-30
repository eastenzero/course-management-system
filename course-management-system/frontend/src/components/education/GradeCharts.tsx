import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Spin, Alert, Typography, Statistic } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

const { Title, Text } = Typography;
const { Option } = Select;

interface GradeDistribution {
  grade: string;
  count: number;
  percentage: number;
  range: string;
}

interface GradeStatistics {
  total_students: number;
  average: number;
  median: number;
  std_dev: number;
  min_score: number;
  max_score: number;
  pass_rate: number;
}

interface CourseGradeData {
  course_info: {
    id: number;
    name: string;
    code: string;
  };
  distribution: Record<string, GradeDistribution>;
  statistics: GradeStatistics;
}

interface StudentTrendData {
  course_id: number;
  course_name: string;
  course_code: string;
  semester: string;
  score: number;
  grade: string;
  enrolled_at: string;
}

interface GradeChartsProps {
  courseId?: number;
  studentId?: number;
  type: 'distribution' | 'trend' | 'comparison';
  data?: any;
  loading?: boolean;
  className?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const GradeCharts: React.FC<GradeChartsProps> = ({
  courseId,
  studentId,
  type,
  data,
  loading = false,
  className
}) => {
  const [chartData, setChartData] = useState<any>(null);
  const [selectedSemester, setSelectedSemester] = useState<string>('all');

  useEffect(() => {
    if (data) {
      setChartData(data);
    }
  }, [data]);

  const renderDistributionChart = (gradeData: CourseGradeData) => {
    const distributionData = Object.entries(gradeData.distribution).map(([grade, info]) => ({
      grade,
      count: info.count,
      percentage: info.percentage,
      range: info.range
    }));

    const pieData = distributionData.filter(item => item.count > 0);

    return (
      <Row gutter={[16, 16]}>
        {/* 统计卡片 */}
        <Col span={24}>
          <Row gutter={16}>
            <Col span={4}>
              <Statistic
                title="总人数"
                value={gradeData.statistics.total_students}
                suffix="人"
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="平均分"
                value={gradeData.statistics.average}
                precision={2}
                suffix="分"
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="及格率"
                value={gradeData.statistics.pass_rate}
                precision={2}
                suffix="%"
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="最高分"
                value={gradeData.statistics.max_score}
                suffix="分"
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="最低分"
                value={gradeData.statistics.min_score}
                suffix="分"
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="标准差"
                value={gradeData.statistics.std_dev}
                precision={2}
              />
            </Col>
          </Row>
        </Col>

        {/* 柱状图 */}
        <Col span={12}>
          <Card title="成绩分布 - 柱状图" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="grade" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    name === 'count' ? `${value}人` : `${value}%`,
                    name === 'count' ? '人数' : '百分比'
                  ]}
                />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" name="人数" />
                <Bar dataKey="percentage" fill="#82ca9d" name="百分比" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 饼图 */}
        <Col span={12}>
          <Card title="成绩分布 - 饼图" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ grade, percentage }) => `${grade}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}人`, '人数']} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    );
  };

  const renderTrendChart = (trendData: any) => {
    const { trend_data, gpa_trend, semester_summary } = trendData;

    // 按学期分组的数据
    const semesterData = Object.entries(semester_summary).map(([semester, info]: [string, any]) => ({
      semester,
      average: info.average,
      course_count: info.course_count,
      total_credits: info.total_credits
    }));

    // GPA趋势数据
    const gpaData = gpa_trend.map((item: any) => ({
      semester: item.semester,
      gpa: item.gpa,
      average: item.average
    }));

    return (
      <Row gutter={[16, 16]}>
        {/* 学期选择 */}
        <Col span={24}>
          <Select
            value={selectedSemester}
            onChange={setSelectedSemester}
            style={{ width: 200, marginBottom: 16 }}
          >
            <Option value="all">所有学期</Option>
            {Object.keys(semester_summary).map(semester => (
              <Option key={semester} value={semester}>{semester}</Option>
            ))}
          </Select>
        </Col>

        {/* 成绩趋势折线图 */}
        <Col span={12}>
          <Card title="学期平均分趋势" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={semesterData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="semester" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="average"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="平均分"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* GPA趋势图 */}
        <Col span={12}>
          <Card title="GPA趋势" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={gpaData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="semester" />
                <YAxis domain={[0, 4]} />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="gpa"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  name="GPA"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 课程数量趋势 */}
        <Col span={24}>
          <Card title="每学期课程数量" size="small">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={semesterData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="semester" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="course_count" fill="#ffc658" name="课程数量" />
                <Bar dataKey="total_credits" fill="#ff7300" name="总学分" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    );
  };

  const renderComparisonChart = (comparisonData: any) => {
    const { course_analysis, student_ranking, class_statistics } = comparisonData;

    // 课程对比数据
    const courseComparisonData = Object.entries(course_analysis).map(([code, info]: [string, any]) => ({
      course_code: code,
      course_name: info.course_name,
      average: info.average,
      pass_rate: info.pass_rate,
      student_count: info.student_count
    }));

    // 学生排名数据（前10名）
    const topStudents = student_ranking.slice(0, 10);

    return (
      <Row gutter={[16, 16]}>
        {/* 班级统计 */}
        <Col span={24}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="班级平均分"
                value={class_statistics.class_average}
                precision={2}
                suffix="分"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="课程数量"
                value={class_statistics.course_count}
                suffix="门"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="参与学生"
                value={comparisonData.class_info.enrolled_student_count}
                suffix="人"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="第一名"
                value={class_statistics.top_student?.student_info.name || '暂无'}
                formatter={(value) => <Text strong>{value}</Text>}
              />
            </Col>
          </Row>
        </Col>

        {/* 课程平均分对比 */}
        <Col span={12}>
          <Card title="各课程平均分对比" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={courseComparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="course_code" />
                <YAxis domain={[0, 100]} />
                <Tooltip
                  formatter={(value, name) => [
                    name === 'average' ? `${value}分` : `${value}%`,
                    name === 'average' ? '平均分' : '及格率'
                  ]}
                />
                <Legend />
                <Bar dataKey="average" fill="#8884d8" name="平均分" />
                <Bar dataKey="pass_rate" fill="#82ca9d" name="及格率" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 学生排名 */}
        <Col span={12}>
          <Card title="学生排名 (前10名)" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topStudents} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="student_info.name" type="category" width={80} />
                <Tooltip formatter={(value) => [`${value}分`, '平均分']} />
                <Bar dataKey="average_score" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    );
  };

  const renderContent = () => {
    if (!chartData) {
      return (
        <Alert
          message="暂无数据"
          description="请选择课程或学生查看相关图表"
          type="info"
          showIcon
        />
      );
    }

    switch (type) {
      case 'distribution':
        return renderDistributionChart(chartData);
      case 'trend':
        return renderTrendChart(chartData);
      case 'comparison':
        return renderComparisonChart(chartData);
      default:
        return null;
    }
  };

  return (
    <div className={className}>
      <Spin spinning={loading}>
        {renderContent()}
      </Spin>
    </div>
  );
};

export default GradeCharts;

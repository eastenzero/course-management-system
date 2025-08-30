import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Select,
  Button,
  Space,
  Typography,
  Tag,
  Statistic,
  Row,
  Col,
  Progress,
  message,
  Empty,
  Spin
} from 'antd';
import {
  TrophyOutlined,
  DownloadOutlined,
  LineChartOutlined,
  BookOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useNavigate } from 'react-router-dom';
import { studentAPI } from '../../../services/studentAPI';

const { Option } = Select;
const { Title, Text } = Typography;

interface GradeRecord {
  id: number;
  course_info: {
    id: number;
    code: string;
    name: string;
  };
  score: number;
  grade: string;
  status: string;
  enrolled_at: string;
}

interface GPAStatistics {
  overall_gpa: number;
  semester_gpa: Record<string, number>;
  credit_summary: {
    total_credits: number;
    completed_credits: number;
    gpa_credits: number;
  };
  grade_distribution: Record<string, number>;
}

const GradesList: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [grades, setGrades] = useState<GradeRecord[]>([]);
  const [gpaStats, setGpaStats] = useState<GPAStatistics | null>(null);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [exporting, setExporting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchGrades();
    fetchGPAStatistics();
  }, [selectedSemester, selectedYear]);

  const fetchGrades = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (selectedSemester) params.semester = selectedSemester;
      if (selectedYear) params.academic_year = selectedYear;
      
      const response = await studentAPI.getGrades(params);
      setGrades(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取成绩失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchGPAStatistics = async () => {
    try {
      const response = await studentAPI.getGPAStatistics();
      setGpaStats(response.data);
    } catch (error: any) {
      console.error('获取GPA统计失败:', error);
    }
  };

  const handleExportGrades = async () => {
    try {
      setExporting(true);
      const params: any = {};
      if (selectedSemester) params.semester = selectedSemester;
      if (selectedYear) params.academic_year = selectedYear;
      
      const response = await studentAPI.exportGrades(params);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `成绩单_${selectedSemester || selectedYear || '全部'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('成绩单导出成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '导出成绩单失败');
    } finally {
      setExporting(false);
    }
  };

  const getGradeColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 70) return '#faad14';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  const getGradeStatus = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 60) return 'processing';
    return 'error';
  };

  const columns: ColumnsType<GradeRecord> = [
    {
      title: '课程信息',
      key: 'course',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {record.course_info.name}
          </div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {record.course_info.code}
          </div>
        </div>
      ),
    },
    {
      title: '成绩',
      key: 'score',
      render: (_, record) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            fontSize: '18px', 
            fontWeight: 'bold', 
            color: getGradeColor(record.score),
            marginBottom: '4px'
          }}>
            {record.score}
          </div>
          <Tag color={getGradeColor(record.score)}>
            {record.grade}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.score - b.score,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          'completed': { color: 'green', text: '已完成' },
          'enrolled': { color: 'blue', text: '进行中' },
          'failed': { color: 'red', text: '未通过' }
        };
        const statusInfo = statusMap[status] || { color: 'default', text: status };
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
      },
    },
    {
      title: '选课时间',
      dataIndex: 'enrolled_at',
      key: 'enrolled_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a, b) => new Date(a.enrolled_at).getTime() - new Date(b.enrolled_at).getTime(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/students/grades/${record.id}`)}
        >
          查看详情
        </Button>
      ),
    },
  ];

  if (loading && !gpaStats) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>成绩查询</Title>
        <Space>
          <Select
            placeholder="选择学年"
            style={{ width: 150 }}
            value={selectedYear}
            onChange={setSelectedYear}
            allowClear
          >
            <Option value="2024-2025">2024-2025学年</Option>
            <Option value="2023-2024">2023-2024学年</Option>
          </Select>
          <Select
            placeholder="选择学期"
            style={{ width: 200 }}
            value={selectedSemester}
            onChange={setSelectedSemester}
            allowClear
          >
            <Option value="2024-2025-1">2024-2025学年第一学期</Option>
            <Option value="2024-2025-2">2024-2025学年第二学期</Option>
          </Select>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={handleExportGrades}
          >
            导出成绩单
          </Button>
        </Space>
      </div>

      {/* GPA统计 */}
      {gpaStats && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总GPA"
                value={gpaStats.overall_gpa}
                precision={2}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: gpaStats.overall_gpa >= 3.0 ? '#52c41a' : '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总学分"
                value={gpaStats.credit_summary.total_credits}
                prefix={<BookOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="已完成学分"
                value={gpaStats.credit_summary.completed_credits}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <div style={{ marginBottom: '8px', color: '#666' }}>学分完成度</div>
                <Progress
                  type="circle"
                  size={80}
                  percent={Math.round((gpaStats.credit_summary.completed_credits / gpaStats.credit_summary.total_credits) * 100)}
                  format={(percent) => `${percent}%`}
                />
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* 成绩分布 */}
      {gpaStats && Object.keys(gpaStats.grade_distribution).length > 0 && (
        <Card title="成绩分布" style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]}>
            {Object.entries(gpaStats.grade_distribution).map(([grade, count]) => (
              <Col xs={12} sm={8} md={6} lg={4} key={grade}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                    {count}
                  </div>
                  <div style={{ color: '#666' }}>{grade}等级</div>
                </div>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 学期GPA趋势 */}
      {gpaStats && Object.keys(gpaStats.semester_gpa).length > 0 && (
        <Card title="学期GPA趋势" style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]}>
            {Object.entries(gpaStats.semester_gpa).map(([semester, gpa]) => (
              <Col xs={12} sm={8} md={6} key={semester}>
                <Card size="small">
                  <Statistic
                    title={semester}
                    value={gpa}
                    precision={2}
                    valueStyle={{ 
                      color: gpa >= 3.5 ? '#52c41a' : gpa >= 3.0 ? '#1890ff' : '#faad14',
                      fontSize: '16px'
                    }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 成绩列表 */}
      <Card title="成绩列表">
        {grades.length === 0 ? (
          <Empty
            description="暂无成绩记录"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={grades}
            rowKey="id"
            loading={loading}
            pagination={{
              total: grades.length,
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条成绩记录`,
            }}
          />
        )}
      </Card>
    </div>
  );
};

export default GradesList;

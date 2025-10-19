import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Select,
  Input,
  Space,
  Typography,
  Tag,
  Modal,
  Form,
  DatePicker,
  Row,
  Col,
  Statistic,
  Tabs,
  message,
  Tooltip,
  Popconfirm,
  Timeline,
} from 'antd';
import {
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileExcelOutlined,
  HistoryOutlined,
  BarChartOutlined,
  FilterOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { gradeApi, courseApi } from '../../../services/api';
import dayjs from 'dayjs';
import { GlassCard } from '../../../components/glass/GlassCard';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

interface GradeRecord {
  id: number;
  student: {
    id: number;
    student_id: string;
    name: string;
    email: string;
    class_name?: string;
  };
  course: {
    id: number;
    name: string;
    code: string;
    semester: string;
  };
  assignment_score?: number;
  midterm_score?: number;
  final_score?: number;
  total_score: number;
  grade: string;
  status: 'draft' | 'submitted' | 'published';
  created_at: string;
  updated_at: string;
  updated_by?: string;
}

interface Course {
  id: number;
  name: string;
  code: string;
  semester: string;
}

interface FilterParams {
  course_id?: number;
  semester?: string;
  grade?: string;
  status?: string;
  student_name?: string;
  date_range?: [string, string];
}

const GradeManagement: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [gradeRecords, setGradeRecords] = useState<GradeRecord[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [filterParams, setFilterParams] = useState<FilterParams>({});
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<GradeRecord | null>(null);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchCourses();
    fetchGradeRecords();
  }, []);

  useEffect(() => {
    fetchGradeRecords();
  }, [filterParams, activeTab]);

  const fetchCourses = async () => {
    try {
      const response = await courseApi.getTeacherCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('获取课程列表失败:', error);
      // 使用模拟数据
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
    }
  };

  const fetchGradeRecords = async () => {
    try {
      setLoading(true);
      const params = {
        ...filterParams,
        status: activeTab === 'all' ? undefined : activeTab,
      };
      const response = await gradeApi.getGradeRecords(params);
      setGradeRecords(response.data);
    } catch (error) {
      console.error('获取成绩记录失败:', error);
      // 使用模拟数据
      const mockGradeRecords: GradeRecord[] = [
        {
          id: 1,
          student: {
            id: 1,
            student_id: '2024001',
            name: '张三',
            email: 'zhangsan@example.com',
            class_name: '计算机科学1班'
          },
          course: {
            id: 1,
            name: '计算机科学导论',
            code: 'CS101',
            semester: '2024-2025-1'
          },
          assignment_score: 85,
          midterm_score: 78,
          final_score: 82,
          total_score: 81,
          grade: 'B',
          status: 'published',
          created_at: '2024-08-01T10:00:00Z',
          updated_at: '2024-08-14T15:30:00Z'
        },
        {
          id: 2,
          student: {
            id: 2,
            student_id: '2024002',
            name: '李四',
            email: 'lisi@example.com',
            class_name: '计算机科学1班'
          },
          course: {
            id: 2,
            name: '数据结构与算法',
            code: 'CS201',
            semester: '2024-2025-1'
          },
          assignment_score: 92,
          midterm_score: 88,
          final_score: 90,
          total_score: 90,
          grade: 'A',
          status: 'published',
          created_at: '2024-08-01T10:00:00Z',
          updated_at: '2024-08-14T16:45:00Z'
        }
      ];
      setGradeRecords(mockGradeRecords);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilterParams(prev => ({
      ...prev,
      student_name: value || undefined,
    }));
  };

  const handleFilterChange = (key: keyof FilterParams, value: any) => {
    setFilterParams(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleResetFilter = () => {
    setFilterParams({});
  };

  const handleViewDetail = (record: GradeRecord) => {
    setSelectedRecord(record);
    setDetailVisible(true);
  };

  const handleViewHistory = (record: GradeRecord) => {
    setSelectedRecord(record);
    setHistoryVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await gradeApi.deleteGrade(id);
      message.success('删除成功');
      fetchGradeRecords();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的记录');
      return;
    }

    Modal.confirm({
      title: '确认删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 条记录吗？`,
      onOk: async () => {
        try {
          await gradeApi.batchDeleteGrades(selectedRowKeys as number[]);
          message.success('批量删除成功');
          setSelectedRowKeys([]);
          fetchGradeRecords();
        } catch (error) {
          message.error('批量删除失败');
        }
      },
    });
  };

  const handleExport = async () => {
    try {
      const params = {
        ...filterParams,
        status: activeTab === 'all' ? undefined : activeTab,
      };
      await gradeApi.exportGrades(params);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const getGradeColor = (grade: string) => {
    const colorMap: Record<string, string> = {
      'A': 'green',
      'B': 'blue',
      'C': 'orange',
      'D': 'gold',
      'F': 'red',
    };
    return colorMap[grade] || 'default';
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      'draft': 'default',
      'submitted': 'processing',
      'published': 'success',
    };
    return colorMap[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
      'draft': '草稿',
      'submitted': '已提交',
      'published': '已发布',
    };
    return textMap[status] || status;
  };

  const columns: ColumnsType<GradeRecord> = [
    {
      title: '学号',
      dataIndex: ['student', 'student_id'],
      key: 'student_id',
      width: 120,
      fixed: 'left',
    },
    {
      title: '姓名',
      dataIndex: ['student', 'name'],
      key: 'student_name',
      width: 100,
      fixed: 'left',
    },
    {
      title: '班级',
      dataIndex: ['student', 'class_name'],
      key: 'class_name',
      width: 120,
    },
    {
      title: '课程',
      key: 'course',
      width: 200,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.course.name}</div>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.course.code} | {record.course.semester}
          </Text>
        </div>
      ),
    },
    {
      title: '平时',
      dataIndex: 'assignment_score',
      key: 'assignment_score',
      width: 80,
      render: (score) => score || '-',
    },
    {
      title: '期中',
      dataIndex: 'midterm_score',
      key: 'midterm_score',
      width: 80,
      render: (score) => score || '-',
    },
    {
      title: '期末',
      dataIndex: 'final_score',
      key: 'final_score',
      width: 80,
      render: (score) => score || '-',
    },
    {
      title: '总分',
      dataIndex: 'total_score',
      key: 'total_score',
      width: 80,
      render: (score) => <Text strong>{score}</Text>,
      sorter: (a, b) => a.total_score - b.total_score,
    },
    {
      title: '等级',
      dataIndex: 'grade',
      key: 'grade',
      width: 80,
      render: (grade) => (
        <Tag color={getGradeColor(grade)}>{grade}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (date) => dayjs(date).format('YYYY-MM-DD HH:mm'),
      sorter: (a, b) => dayjs(a.updated_at).unix() - dayjs(b.updated_at).unix(),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="link"
              icon={<EditOutlined />}
              size="small"
              disabled={record.status === 'published'}
            />
          </Tooltip>
          <Tooltip title="历史记录">
            <Button
              type="link"
              icon={<HistoryOutlined />}
              onClick={() => handleViewHistory(record)}
              size="small"
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="link"
                icon={<DeleteOutlined />}
                danger
                size="small"
                disabled={record.status === 'published'}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
    getCheckboxProps: (record: GradeRecord) => ({
      disabled: record.status === 'published',
    }),
  };

  const getTabCounts = () => {
    const counts = gradeRecords.reduce((acc, record) => {
      acc[record.status] = (acc[record.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      all: gradeRecords.length,
      draft: counts.draft || 0,
      submitted: counts.submitted || 0,
      published: counts.published || 0,
    };
  };

  const tabCounts = getTabCounts();

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
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>成绩管理</Title>
        
        {/* 筛选器 */}
        <Card style={{ marginBottom: '16px' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Select
                placeholder="选择课程"
                style={{ width: '100%' }}
                value={filterParams.course_id}
                onChange={(value) => handleFilterChange('course_id', value)}
                allowClear
              >
                {courses.map(course => (
                  <Option key={course.id} value={course.id}>
                    {course.name}
                  </Option>
                ))}
              </Select>
            </Col>
            
            <Col xs={24} sm={12} md={6}>
              <Select
                placeholder="选择学期"
                style={{ width: '100%' }}
                value={filterParams.semester}
                onChange={(value) => handleFilterChange('semester', value)}
                allowClear
              >
                <Option value="2024-2025-1">2024-2025学年第一学期</Option>
                <Option value="2024-2025-2">2024-2025学年第二学期</Option>
              </Select>
            </Col>
            
            <Col xs={24} sm={12} md={6}>
              <Select
                placeholder="选择等级"
                style={{ width: '100%' }}
                value={filterParams.grade}
                onChange={(value) => handleFilterChange('grade', value)}
                allowClear
              >
                <Option value="A">A</Option>
                <Option value="B">B</Option>
                <Option value="C">C</Option>
                <Option value="D">D</Option>
                <Option value="F">F</Option>
              </Select>
            </Col>
            
            <Col xs={24} sm={12} md={6}>
              <Search
                placeholder="搜索学生姓名"
                onSearch={handleSearch}
                allowClear
              />
            </Col>
            
            <Col xs={24} md={12}>
              <RangePicker
                style={{ width: '100%' }}
                onChange={(dates) => {
                  if (dates) {
                    handleFilterChange('date_range', [
                      dates[0]?.format('YYYY-MM-DD'),
                      dates[1]?.format('YYYY-MM-DD'),
                    ]);
                  } else {
                    handleFilterChange('date_range', undefined);
                  }
                }}
              />
            </Col>
            
            <Col xs={24} md={12}>
              <Space>
                <Button
                  icon={<FilterOutlined />}
                  onClick={handleResetFilter}
                >
                  重置筛选
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={fetchGradeRecords}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 操作按钮 */}
        <div style={{ marginBottom: '16px' }}>
          <Space>
            <Button
              type="primary"
              danger
              icon={<DeleteOutlined />}
              onClick={handleBatchDelete}
              disabled={selectedRowKeys.length === 0}
            >
              批量删除 ({selectedRowKeys.length})
            </Button>
            <Button
              icon={<FileExcelOutlined />}
              onClick={handleExport}
            >
              导出Excel
            </Button>
            <Button
              icon={<BarChartOutlined />}
            >
              统计分析
            </Button>
          </Space>
        </div>
      </div>

      {/* 成绩列表 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab={`全部 (${tabCounts.all})`} key="all" />
          <TabPane tab={`草稿 (${tabCounts.draft})`} key="draft" />
          <TabPane tab={`已提交 (${tabCounts.submitted})`} key="submitted" />
          <TabPane tab={`已发布 (${tabCounts.published})`} key="published" />
        </Tabs>

        <Table
          columns={columns}
          dataSource={gradeRecords}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          scroll={{ x: 1400 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="成绩详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedRecord && (
          <div>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="学号" value={selectedRecord.student.student_id} />
              </Col>
              <Col span={12}>
                <Statistic title="姓名" value={selectedRecord.student.name} />
              </Col>
              <Col span={12}>
                <Statistic title="课程" value={selectedRecord.course.name} />
              </Col>
              <Col span={12}>
                <Statistic title="课程代码" value={selectedRecord.course.code} />
              </Col>
              <Col span={8}>
                <Statistic title="平时成绩" value={selectedRecord.assignment_score || '-'} />
              </Col>
              <Col span={8}>
                <Statistic title="期中成绩" value={selectedRecord.midterm_score || '-'} />
              </Col>
              <Col span={8}>
                <Statistic title="期末成绩" value={selectedRecord.final_score || '-'} />
              </Col>
              <Col span={12}>
                <Statistic title="总成绩" value={selectedRecord.total_score} />
              </Col>
              <Col span={12}>
                <div>
                  <Text>等级: </Text>
                  <Tag color={getGradeColor(selectedRecord.grade)}>
                    {selectedRecord.grade}
                  </Tag>
                </div>
              </Col>
            </Row>
          </div>
        )}
      </Modal>

      {/* 历史记录弹窗 */}
      <Modal
        title="修改历史"
        open={historyVisible}
        onCancel={() => setHistoryVisible(false)}
        footer={null}
        width={800}
      >
        <Timeline>
          <Timeline.Item color="green">
            <p>初始成绩录入</p>
            <p>时间: 2024-08-14 09:30:00</p>
            <p>操作人: 张教授</p>
            <p>成绩: 85分</p>
          </Timeline.Item>
          <Timeline.Item color="blue">
            <p>成绩修改</p>
            <p>时间: 2024-08-14 14:20:00</p>
            <p>操作人: 张教授</p>
            <p>修改后: 88分 (原: 85分)</p>
            <p>原因: 学生申请复查</p>
          </Timeline.Item>
          <Timeline.Item color="orange">
            <p>成绩发布</p>
            <p>时间: 2024-08-14 16:00:00</p>
            <p>操作人: 张教授</p>
            <p>状态: 已发布</p>
          </Timeline.Item>
        </Timeline>
      </Modal>
      </div>
    </div>
  );
};

export default GradeManagement;

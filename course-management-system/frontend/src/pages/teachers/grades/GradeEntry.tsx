import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Input,
  Button,
  Select,
  Form,
  InputNumber,
  message,
  Space,
  Typography,
  Tag,
  Modal,
  Row,
  Col,
  Statistic,
  Progress,
} from 'antd';
import {
  SaveOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  BarChartOutlined,
  FileExcelOutlined,
  ImportOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { gradeApi, courseApi } from '../../../services/api';
import { GlassCard } from '../../../components/glass/GlassCard';
import DynamicBackground from '../../../components/common/DynamicBackground';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Title, Text } = Typography;
const { Option } = Select;

interface Student {
  id: number;
  student_id: string;
  name: string;
  email: string;
  class_name?: string;
}

interface GradeRecord {
  id?: number;
  student: Student;
  course_id: number;
  assignment_score?: number;
  midterm_score?: number;
  final_score?: number;
  total_score?: number;
  grade?: string;
  status: 'draft' | 'submitted' | 'published';
  updated_at?: string;
}

interface Course {
  id: number;
  name: string;
  code: string;
  semester: string;
}

const GradeEntry: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [gradeRecords, setGradeRecords] = useState<GradeRecord[]>([]);
  const [editingKey, setEditingKey] = useState<number | null>(null);
  const [statisticsVisible, setStatisticsVisible] = useState(false);

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      fetchGradeRecords();
    }
  }, [selectedCourse]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await courseApi.getTeacherCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('获取课程列表失败:', error);
      // 使用模拟数据
      const mockCourses: Course[] = [
        { id: 1, name: '计算机科学导论', code: 'CS101', semester: '2024-2025-1' },
        { id: 2, name: '数据结构与算法', code: 'CS201', semester: '2024-2025-1' }
      ];
      setCourses(mockCourses);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const fetchGradeRecords = async () => {
    if (!selectedCourse) return;
    
    try {
      setLoading(true);
      const response = await gradeApi.getCourseGrades(selectedCourse);
      setGradeRecords(response.data);
    } catch (error) {
      console.error('获取成绩记录失败:', error);
      // 使用模拟数据
      const mockGradeRecords: GradeRecord[] = [
        {
          id: 1,
          student: {
            id: 1,
            student_id: 'S2023001',
            name: '张三',
            email: 'zhangsan@example.com',
            class_name: '计科一班'
          },
          course_id: selectedCourse,
          assignment_score: 85,
          midterm_score: 78,
          final_score: 92,
          total_score: 85,
          grade: 'B',
          status: 'draft'
        },
        {
          id: 2,
          student: {
            id: 2,
            student_id: 'S2023002',
            name: '李四',
            email: 'lisi@example.com',
            class_name: '计科一班'
          },
          course_id: selectedCourse,
          assignment_score: 92,
          midterm_score: 88,
          final_score: 95,
          total_score: 92,
          grade: 'A',
          status: 'draft'
        }
      ];
      setGradeRecords(mockGradeRecords);
      message.info('正在使用模拟数据，请启动后端服务获取真实数据');
    } finally {
      setLoading(false);
    }
  };

  const calculateTotalScore = (record: GradeRecord) => {
    const assignment = record.assignment_score || 0;
    const midterm = record.midterm_score || 0;
    const final = record.final_score || 0;
    
    // 平时成绩30% + 期中成绩30% + 期末成绩40%
    return Math.round(assignment * 0.3 + midterm * 0.3 + final * 0.4);
  };

  const getGrade = (totalScore: number) => {
    if (totalScore >= 90) return 'A';
    if (totalScore >= 80) return 'B';
    if (totalScore >= 70) return 'C';
    if (totalScore >= 60) return 'D';
    return 'F';
  };

  const getGradeColor = (grade: string) => {
    const colorMap: Record<string, string> = {
      'A': '#52c41a',
      'B': '#1890ff',
      'C': '#faad14',
      'D': '#fa8c16',
      'F': '#f5222d',
    };
    return colorMap[grade] || '#d9d9d9';
  };

  const handleEdit = (record: GradeRecord) => {
    setEditingKey(record.student.id);
    form.setFieldsValue({
      [`assignment_${record.student.id}`]: record.assignment_score,
      [`midterm_${record.student.id}`]: record.midterm_score,
      [`final_${record.student.id}`]: record.final_score,
    });
  };

  const handleSave = async (studentId: number) => {
    try {
      const values = await form.validateFields([
        `assignment_${studentId}`,
        `midterm_${studentId}`,
        `final_${studentId}`,
      ]);

      setSaving(true);
      
      const gradeData = {
        student_id: studentId,
        course_id: selectedCourse,
        assignment_score: values[`assignment_${studentId}`],
        midterm_score: values[`midterm_${studentId}`],
        final_score: values[`final_${studentId}`],
      };

      await gradeApi.updateGrade(gradeData);
      message.success('成绩保存成功');
      setEditingKey(null);
      fetchGradeRecords();
    } catch (error) {
      message.error('保存成绩失败');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingKey(null);
    form.resetFields();
  };

  const handleBatchSave = async () => {
    try {
      setSaving(true);
      const updates = gradeRecords
        .filter(record => record.status === 'draft')
        .map(record => ({
          student_id: record.student.id,
          course_id: selectedCourse,
          assignment_score: record.assignment_score,
          midterm_score: record.midterm_score,
          final_score: record.final_score,
        }));

      await gradeApi.batchUpdateGrades(updates);
      message.success('批量保存成功');
      fetchGradeRecords();
    } catch (error) {
      message.error('批量保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handlePublishGrades = async () => {
    Modal.confirm({
      title: '确认发布成绩',
      content: '发布后学生将能够查看成绩，确定要发布吗？',
      onOk: async () => {
        try {
          await gradeApi.publishGrades(selectedCourse!);
          message.success('成绩发布成功');
          fetchGradeRecords();
        } catch (error) {
          message.error('成绩发布失败');
        }
      },
    });
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
      key: 'name',
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
      title: '平时成绩',
      key: 'assignment_score',
      width: 120,
      render: (_, record) => {
        const isEditing = editingKey === record.student.id;
        return isEditing ? (
          <Form.Item
            name={`assignment_${record.student.id}`}
            style={{ margin: 0 }}
            rules={[
              { type: 'number', min: 0, max: 100, message: '请输入0-100的数字' }
            ]}
          >
            <InputNumber
              min={0}
              max={100}
              precision={1}
              style={{ width: '100%' }}
            />
          </Form.Item>
        ) : (
          <Text>{record.assignment_score || '-'}</Text>
        );
      },
    },
    {
      title: '期中成绩',
      key: 'midterm_score',
      width: 120,
      render: (_, record) => {
        const isEditing = editingKey === record.student.id;
        return isEditing ? (
          <Form.Item
            name={`midterm_${record.student.id}`}
            style={{ margin: 0 }}
            rules={[
              { type: 'number', min: 0, max: 100, message: '请输入0-100的数字' }
            ]}
          >
            <InputNumber
              min={0}
              max={100}
              precision={1}
              style={{ width: '100%' }}
            />
          </Form.Item>
        ) : (
          <Text>{record.midterm_score || '-'}</Text>
        );
      },
    },
    {
      title: '期末成绩',
      key: 'final_score',
      width: 120,
      render: (_, record) => {
        const isEditing = editingKey === record.student.id;
        return isEditing ? (
          <Form.Item
            name={`final_${record.student.id}`}
            style={{ margin: 0 }}
            rules={[
              { type: 'number', min: 0, max: 100, message: '请输入0-100的数字' }
            ]}
          >
            <InputNumber
              min={0}
              max={100}
              precision={1}
              style={{ width: '100%' }}
            />
          </Form.Item>
        ) : (
          <Text>{record.final_score || '-'}</Text>
        );
      },
    },
    {
      title: '总成绩',
      key: 'total_score',
      width: 100,
      render: (_, record) => {
        const total = record.total_score || calculateTotalScore(record);
        return <Text strong>{total}</Text>;
      },
    },
    {
      title: '等级',
      key: 'grade',
      width: 80,
      render: (_, record) => {
        const total = record.total_score || calculateTotalScore(record);
        const grade = record.grade || getGrade(total);
        return (
          <Tag color={getGradeColor(grade)}>
            {grade}
          </Tag>
        );
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap = {
          'draft': { text: '草稿', color: 'default' },
          'submitted': { text: '已提交', color: 'processing' },
          'published': { text: '已发布', color: 'success' },
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => {
        const isEditing = editingKey === record.student.id;
        
        if (isEditing) {
          return (
            <Space>
              <Button
                type="link"
                icon={<CheckOutlined />}
                onClick={() => handleSave(record.student.id)}
                loading={saving}
                size="small"
              >
                保存
              </Button>
              <Button
                type="link"
                icon={<CloseOutlined />}
                onClick={handleCancel}
                size="small"
              >
                取消
              </Button>
            </Space>
          );
        }

        return (
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
            disabled={record.status === 'published'}
          >
            编辑
          </Button>
        );
      },
    },
  ];

  const getStatistics = () => {
    if (!gradeRecords.length) return null;

    const scores = gradeRecords
      .map(record => record.total_score || calculateTotalScore(record))
      .filter(score => score > 0);

    if (!scores.length) return null;

    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    const passCount = scores.filter(score => score >= 60).length;
    const passRate = (passCount / scores.length) * 100;

    const gradeDistribution = scores.reduce((acc, score) => {
      const grade = getGrade(score);
      acc[grade] = (acc[grade] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      average: Math.round(average * 10) / 10,
      passRate: Math.round(passRate * 10) / 10,
      total: scores.length,
      passCount,
      gradeDistribution,
    };
  };

  const statistics = getStatistics();

  return (
    <div className="glass-page-background">
      <DynamicBackground
        density={0.08}
        speed={0.8}
        lineMaxDist={120}
        triMaxDist={80}
      />
      
      <div className="glass-content" style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>成绩录入</Title>
        
        <Row gutter={16} style={{ marginBottom: '16px' }}>
          <Col xs={24} sm={12} md={8}>
            <Select
              placeholder="选择课程"
              style={{ width: '100%' }}
              value={selectedCourse}
              onChange={setSelectedCourse}
              loading={loading}
            >
              {courses.map(course => (
                <Option key={course.id} value={course.id}>
                  {course.name} ({course.code})
                </Option>
              ))}
            </Select>
          </Col>
          
          {selectedCourse && (
            <Col xs={24} sm={12} md={16}>
              <Space>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={handleBatchSave}
                  loading={saving}
                >
                  批量保存
                </Button>
                <Button
                  icon={<CheckOutlined />}
                  onClick={handlePublishGrades}
                >
                  发布成绩
                </Button>
                <Button
                  icon={<BarChartOutlined />}
                  onClick={() => setStatisticsVisible(true)}
                >
                  统计分析
                </Button>
                <Button icon={<FileExcelOutlined />}>
                  导出Excel
                </Button>
                <Button icon={<ImportOutlined />}>
                  导入成绩
                </Button>
              </Space>
            </Col>
          )}
        </Row>
      </div>

      {selectedCourse && (
        <Card>
          <Form form={form} component={false}>
            <Table
              columns={columns}
              dataSource={gradeRecords}
              rowKey={record => record.student.id}
              loading={loading}
              scroll={{ x: 1200 }}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
          </Form>
        </Card>
      )}

      {/* 统计分析弹窗 */}
      <Modal
        title="成绩统计分析"
        open={statisticsVisible}
        onCancel={() => setStatisticsVisible(false)}
        footer={null}
        width={600}
      >
        {statistics && (
          <Row gutter={[16, 16]}>
            <Col xs={12} sm={6}>
              <Statistic
                title="平均分"
                value={statistics.average}
                precision={1}
                suffix="分"
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="及格率"
                value={statistics.passRate}
                precision={1}
                suffix="%"
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="总人数"
                value={statistics.total}
                suffix="人"
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="及格人数"
                value={statistics.passCount}
                suffix="人"
              />
            </Col>
            
            <Col span={24}>
              <Title level={5}>成绩分布</Title>
              {Object.entries(statistics.gradeDistribution).map(([grade, count]) => (
                <div key={grade} style={{ marginBottom: '8px' }}>
                  <Text>{grade}等级: {count}人</Text>
                  <Progress
                    percent={(count / statistics.total) * 100}
                    strokeColor={getGradeColor(grade)}
                    showInfo={false}
                    size="small"
                  />
                </div>
              ))}
            </Col>
          </Row>
        )}
      </Modal>
      </div>
    </div>
  );
};

export default GradeEntry;

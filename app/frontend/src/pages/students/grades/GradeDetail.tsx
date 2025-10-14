import React, { useState, useEffect } from 'react';
import {
  Card,
  Descriptions,
  Table,
  Typography,
  Tag,
  Progress,
  Button,
  Space,
  Spin,
  message,
  Alert,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  ArrowLeftOutlined,
  TrophyOutlined,
  BookOutlined,
  CalendarOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface GradeDetail {
  id: number;
  enrollment_id: number;
  student_info: {
    id: number;
    username: string;
    name: string;
    student_id: string;
  };
  course_info: {
    id: number;
    code: string;
    name: string;
  };
  detailed_grades: Array<{
    id: number;
    grade_type: string;
    grade_type_display: string;
    name: string;
    score: number;
    max_score: number;
    percentage_score: number;
    letter_grade: string;
    weight: number;
    graded_at: string;
    feedback: string;
  }>;
  final_score: number;
  final_grade: string;
  grade_breakdown: Record<string, any[]>;
}

const GradeDetail: React.FC = () => {
  const { enrollmentId } = useParams<{ enrollmentId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [gradeDetail, setGradeDetail] = useState<GradeDetail | null>(null);

  useEffect(() => {
    if (enrollmentId) {
      fetchGradeDetail();
    }
  }, [enrollmentId]);

  const fetchGradeDetail = async () => {
    try {
      setLoading(true);
      // 这里应该调用API获取成绩详情
      // 暂时使用模拟数据
      const mockData: GradeDetail = {
        id: 1,
        enrollment_id: parseInt(enrollmentId || '1'),
        student_info: {
          id: 1,
          username: 'student001',
          name: '张三',
          student_id: '2024001'
        },
        course_info: {
          id: 1,
          code: 'CS101',
          name: '计算机科学导论'
        },
        detailed_grades: [
          {
            id: 1,
            grade_type: 'assignment',
            grade_type_display: '作业',
            name: '第一次作业',
            score: 85,
            max_score: 100,
            percentage_score: 85,
            letter_grade: 'B',
            weight: 20,
            graded_at: '2024-03-15T10:00:00Z',
            feedback: '完成质量良好，逻辑清晰'
          },
          {
            id: 2,
            grade_type: 'midterm',
            grade_type_display: '期中考试',
            name: '期中考试',
            score: 78,
            max_score: 100,
            percentage_score: 78,
            letter_grade: 'C',
            weight: 30,
            graded_at: '2024-04-20T14:00:00Z',
            feedback: '基础知识掌握较好，需加强应用能力'
          },
          {
            id: 3,
            grade_type: 'final',
            grade_type_display: '期末考试',
            name: '期末考试',
            score: 88,
            max_score: 100,
            percentage_score: 88,
            letter_grade: 'B',
            weight: 40,
            graded_at: '2024-06-25T09:00:00Z',
            feedback: '综合表现优秀，继续保持'
          },
          {
            id: 4,
            grade_type: 'participation',
            grade_type_display: '课堂参与',
            name: '课堂表现',
            score: 92,
            max_score: 100,
            percentage_score: 92,
            letter_grade: 'A',
            weight: 10,
            graded_at: '2024-06-30T16:00:00Z',
            feedback: '积极参与课堂讨论，表现突出'
          }
        ],
        final_score: 83.2,
        final_grade: 'B',
        grade_breakdown: {
          '作业': [
            {
              name: '第一次作业',
              score: 85,
              max_score: 100,
              percentage: 85,
              weight: 20
            }
          ],
          '期中考试': [
            {
              name: '期中考试',
              score: 78,
              max_score: 100,
              percentage: 78,
              weight: 30
            }
          ],
          '期末考试': [
            {
              name: '期末考试',
              score: 88,
              max_score: 100,
              percentage: 88,
              weight: 40
            }
          ],
          '课堂参与': [
            {
              name: '课堂表现',
              score: 92,
              max_score: 100,
              percentage: 92,
              weight: 10
            }
          ]
        }
      };
      
      setGradeDetail(mockData);
    } catch (error: any) {
      message.error('获取成绩详情失败');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 70) return '#faad14';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  const columns: ColumnsType<any> = [
    {
      title: '评分项目',
      key: 'item',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.name}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.grade_type_display}
          </div>
        </div>
      ),
    },
    {
      title: '得分',
      key: 'score',
      render: (_, record) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '16px', fontWeight: 'bold', color: getGradeColor(record.percentage_score) }}>
            {record.score}/{record.max_score}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.percentage_score}%
          </div>
        </div>
      ),
    },
    {
      title: '等级',
      dataIndex: 'letter_grade',
      key: 'letter_grade',
      render: (grade: string, record) => (
        <Tag color={getGradeColor(record.percentage_score)}>
          {grade}
        </Tag>
      ),
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (weight: number) => `${weight}%`,
    },
    {
      title: '评分时间',
      dataIndex: 'graded_at',
      key: 'graded_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '评语',
      dataIndex: 'feedback',
      key: 'feedback',
      render: (feedback: string) => (
        <div style={{ maxWidth: '200px' }}>
          {feedback || '暂无评语'}
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!gradeDetail) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="未找到成绩详情"
          description="请检查链接是否正确或联系管理员"
          type="error"
          showIcon
        />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/students/grades')}
          style={{ marginBottom: '16px' }}
        >
          返回成绩列表
        </Button>
        <Title level={2}>成绩详情</Title>
      </div>

      {/* 课程基本信息 */}
      <Card title="课程信息" style={{ marginBottom: '24px' }}>
        <Descriptions column={2}>
          <Descriptions.Item label="课程名称">
            {gradeDetail.course_info.name}
          </Descriptions.Item>
          <Descriptions.Item label="课程代码">
            {gradeDetail.course_info.code}
          </Descriptions.Item>
          <Descriptions.Item label="学生姓名">
            {gradeDetail.student_info.name}
          </Descriptions.Item>
          <Descriptions.Item label="学号">
            {gradeDetail.student_info.student_id}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 总成绩概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="最终成绩"
              value={gradeDetail.final_score}
              precision={1}
              suffix="分"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: getGradeColor(gradeDetail.final_score) }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '8px', color: '#666' }}>等级</div>
              <Tag 
                style={{ fontSize: '18px', padding: '8px 16px' }}
                color={getGradeColor(gradeDetail.final_score)}
              >
                {gradeDetail.final_grade}
              </Tag>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '8px', color: '#666' }}>成绩进度</div>
              <Progress
                type="circle"
                size={80}
                percent={gradeDetail.final_score}
                format={(percent) => `${percent}%`}
                strokeColor={getGradeColor(gradeDetail.final_score)}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 成绩构成 */}
      <Card title="成绩构成" style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          {Object.entries(gradeDetail.grade_breakdown).map(([type, items]) => (
            <Col xs={24} sm={12} lg={6} key={type}>
              <Card size="small" title={type}>
                {items.map((item, index) => (
                  <div key={index} style={{ marginBottom: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text>{item.name}</Text>
                      <Text strong style={{ color: getGradeColor(item.percentage) }}>
                        {item.score}/{item.max_score}
                      </Text>
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      权重: {item.weight}% | 得分率: {item.percentage}%
                    </div>
                  </div>
                ))}
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 详细成绩表 */}
      <Card title="详细成绩">
        <Table
          columns={columns}
          dataSource={gradeDetail.detailed_grades}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default GradeDetail;

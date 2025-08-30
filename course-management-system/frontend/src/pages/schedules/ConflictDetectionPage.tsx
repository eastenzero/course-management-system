import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Table,
  Button,
  Space,
  Select,
  Alert,
  Tag,
  Row,
  Col,
  Statistic,
  Empty,
  Tooltip,
} from 'antd';
import {
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

interface Schedule {
  id: string;
  courseCode: string;
  courseName: string;
  teacher: string;
  classroom: string;
  dayOfWeek: number;
  startTime: string;
  endTime: string;
  weeks: string;
  semester: string;
}

interface Conflict {
  id: string;
  type: 'teacher' | 'classroom' | 'time';
  severity: 'high' | 'medium' | 'low';
  description: string;
  schedules: Schedule[];
  suggestion?: string;
}

const ConflictDetectionPage: React.FC = () => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [selectedSemester, setSelectedSemester] = useState('2024-1');
  const [loading, setLoading] = useState(false);

  // 模拟数据
  useEffect(() => {
    const mockSchedules: Schedule[] = [
      {
        id: '1',
        courseCode: 'MATH101',
        courseName: '高等数学',
        teacher: '张教授',
        classroom: 'A101',
        dayOfWeek: 1,
        startTime: '08:00',
        endTime: '09:40',
        weeks: '1-16',
        semester: '2024-1',
      },
      {
        id: '2',
        courseCode: 'CS201',
        courseName: '数据结构',
        teacher: '张教授', // 同一教师
        classroom: 'B205',
        dayOfWeek: 1, // 同一天
        startTime: '08:30', // 时间重叠
        endTime: '10:10',
        weeks: '1-16',
        semester: '2024-1',
      },
      {
        id: '3',
        courseCode: 'ENG101',
        courseName: '大学英语',
        teacher: '王老师',
        classroom: 'A101', // 同一教室
        dayOfWeek: 1, // 同一天
        startTime: '09:00', // 时间重叠
        endTime: '10:40',
        weeks: '1-16',
        semester: '2024-1',
      },
    ];
    setSchedules(mockSchedules);
  }, []);

  // 检测冲突
  useEffect(() => {
    detectConflicts();
  }, [schedules, selectedSemester]);

  const detectConflicts = () => {
    setLoading(true);
    const semesterSchedules = schedules.filter(s => s.semester === selectedSemester);
    const detectedConflicts: Conflict[] = [];

    // 检测教师冲突
    for (let i = 0; i < semesterSchedules.length; i++) {
      for (let j = i + 1; j < semesterSchedules.length; j++) {
        const schedule1 = semesterSchedules[i];
        const schedule2 = semesterSchedules[j];

        // 教师时间冲突
        if (
          schedule1.teacher === schedule2.teacher &&
          schedule1.dayOfWeek === schedule2.dayOfWeek &&
          isTimeOverlap(schedule1, schedule2)
        ) {
          detectedConflicts.push({
            id: `teacher-${schedule1.id}-${schedule2.id}`,
            type: 'teacher',
            severity: 'high',
            description: `教师 ${schedule1.teacher} 在 ${getWeekDay(schedule1.dayOfWeek)} ${schedule1.startTime}-${schedule1.endTime} 时间段有冲突`,
            schedules: [schedule1, schedule2],
            suggestion: '建议调整其中一门课程的时间安排'
          });
        }

        // 教室冲突
        if (
          schedule1.classroom === schedule2.classroom &&
          schedule1.dayOfWeek === schedule2.dayOfWeek &&
          isTimeOverlap(schedule1, schedule2)
        ) {
          detectedConflicts.push({
            id: `classroom-${schedule1.id}-${schedule2.id}`,
            type: 'classroom',
            severity: 'high',
            description: `教室 ${schedule1.classroom} 在 ${getWeekDay(schedule1.dayOfWeek)} ${schedule1.startTime}-${schedule1.endTime} 时间段有冲突`,
            schedules: [schedule1, schedule2],
            suggestion: '建议更换其中一门课程的教室'
          });
        }
      }
    }

    setConflicts(detectedConflicts);
    setLoading(false);
  };

  const isTimeOverlap = (schedule1: Schedule, schedule2: Schedule): boolean => {
    const start1 = timeToMinutes(schedule1.startTime);
    const end1 = timeToMinutes(schedule1.endTime);
    const start2 = timeToMinutes(schedule2.startTime);
    const end2 = timeToMinutes(schedule2.endTime);

    return !(end1 <= start2 || end2 <= start1);
  };

  const timeToMinutes = (time: string): number => {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
  };

  const getWeekDay = (dayOfWeek: number): string => {
    const weekDays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return weekDays[dayOfWeek];
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'yellow';
      default: return 'default';
    }
  };

  const getSeverityText = (severity: string): string => {
    switch (severity) {
      case 'high': return '严重';
      case 'medium': return '中等';
      case 'low': return '轻微';
      default: return '未知';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'teacher': return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'classroom': return <WarningOutlined style={{ color: '#faad14' }} />;
      default: return <ExclamationCircleOutlined />;
    }
  };

  const columns = [
    {
      title: '冲突类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => (
        <Space>
          {getTypeIcon(type)}
          <span>{type === 'teacher' ? '教师冲突' : '教室冲突'}</span>
        </Space>
      ),
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>
          {getSeverityText(severity)}
        </Tag>
      ),
    },
    {
      title: '冲突描述',
      dataIndex: 'description',
      key: 'description',
      width: 300,
    },
    {
      title: '涉及课程',
      dataIndex: 'schedules',
      key: 'schedules',
      width: 200,
      render: (schedules: Schedule[]) => (
        <div>
          {schedules.map(schedule => (
            <Tag key={schedule.id} color="blue" style={{ marginBottom: '2px' }}>
              {schedule.courseCode}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: '建议',
      dataIndex: 'suggestion',
      key: 'suggestion',
      render: (suggestion: string) => (
        <Tooltip title={suggestion}>
          <span style={{ color: '#666' }}>
            {suggestion ? suggestion.substring(0, 20) + '...' : '暂无建议'}
          </span>
        </Tooltip>
      ),
    },
  ];

  const handleRecheck = () => {
    detectConflicts();
  };

  const conflictStats = {
    total: conflicts.length,
    high: conflicts.filter(c => c.severity === 'high').length,
    medium: conflicts.filter(c => c.severity === 'medium').length,
    low: conflicts.filter(c => c.severity === 'low').length,
  };

  return (
    <div className="conflict-detection-page">
      <div className="page-header">
        <Title level={2}>冲突检测</Title>
        <p>自动检测课程安排中的时间冲突和资源冲突</p>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总冲突数"
              value={conflictStats.total}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: conflictStats.total > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="严重冲突"
              value={conflictStats.high}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="中等冲突"
              value={conflictStats.medium}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="轻微冲突"
              value={conflictStats.low}
              valueStyle={{ color: '#fadb14' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Select
              value={selectedSemester}
              onChange={setSelectedSemester}
              style={{ width: '100%' }}
              placeholder="选择学期"
            >
              <Option value="2024-1">2024年春季学期</Option>
              <Option value="2024-2">2024年秋季学期</Option>
              <Option value="2025-1">2025年春季学期</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={16} style={{ textAlign: 'right' }}>
            <Space>
              <Button 
                icon={<ReloadOutlined />}
                onClick={handleRecheck}
                loading={loading}
              >
                重新检测
              </Button>
              <Button 
                icon={<SettingOutlined />}
                type="primary"
              >
                检测设置
              </Button>
            </Space>
          </Col>
        </Row>

        {conflicts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={4} style={{ color: '#52c41a' }}>
              未发现冲突
            </Title>
            <p style={{ color: '#666' }}>
              当前学期的课程安排没有发现时间或资源冲突
            </p>
          </div>
        ) : (
          <>
            <Alert
              message={`发现 ${conflicts.length} 个冲突`}
              description="请及时处理以下冲突，确保课程安排的合理性"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Table
              columns={columns}
              dataSource={conflicts}
              rowKey="id"
              loading={loading}
              pagination={{
                total: conflicts.length,
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 个冲突`,
              }}
            />
          </>
        )}
      </Card>
    </div>
  );
};

export default ConflictDetectionPage;

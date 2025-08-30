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
  Badge,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  HomeOutlined,
  CalendarOutlined,
  BarChartOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Title } = Typography;
const { TabPane } = Tabs;

interface Classroom {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  type: 'lecture' | 'lab' | 'seminar' | 'computer' | 'multimedia';
  equipment: string[];
  isAvailable: boolean;
  description?: string;
}

interface Schedule {
  id: string;
  courseCode: string;
  courseName: string;
  teacher: string;
  dayOfWeek: number;
  startTime: string;
  endTime: string;
  weeks: string;
}

const ClassroomDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [classroom, setClassroom] = useState<Classroom | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 模拟API调用获取教室详情
    const fetchClassroomDetail = async () => {
      try {
        setLoading(true);
        
        // 模拟数据
        const mockClassroom: Classroom = {
          id: id || '1',
          name: 'A101',
          building: 'A栋',
          floor: 1,
          capacity: 120,
          type: 'lecture',
          equipment: ['投影仪', '音响', '黑板', '讲台', '空调'],
          isAvailable: true,
          description: '大型阶梯教室，适合大班授课。配备先进的多媒体设备，音响效果良好。',
        };

        const mockSchedules: Schedule[] = [
          {
            id: '1',
            courseCode: 'MATH101',
            courseName: '高等数学',
            teacher: '张教授',
            dayOfWeek: 1,
            startTime: '08:00',
            endTime: '09:40',
            weeks: '1-16',
          },
          {
            id: '2',
            courseCode: 'PHY101',
            courseName: '大学物理',
            teacher: '李教授',
            dayOfWeek: 3,
            startTime: '10:00',
            endTime: '11:40',
            weeks: '1-16',
          },
          {
            id: '3',
            courseCode: 'CHEM101',
            courseName: '无机化学',
            teacher: '王教授',
            dayOfWeek: 5,
            startTime: '14:00',
            endTime: '15:40',
            weeks: '1-16',
          },
        ];

        setClassroom(mockClassroom);
        setSchedules(mockSchedules);
      } catch (error) {
        message.error('获取教室详情失败');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchClassroomDetail();
    }
  }, [id]);

  const getTypeText = (type: string): string => {
    const typeMap = {
      lecture: '阶梯教室',
      lab: '实验室',
      seminar: '研讨室',
      computer: '机房',
      multimedia: '多媒体教室',
    };
    return typeMap[type as keyof typeof typeMap] || type;
  };

  const getTypeColor = (type: string): string => {
    const colorMap = {
      lecture: 'blue',
      lab: 'green',
      seminar: 'orange',
      computer: 'purple',
      multimedia: 'cyan',
    };
    return colorMap[type as keyof typeof colorMap] || 'default';
  };

  const getWeekDay = (dayOfWeek: number): string => {
    const weekDays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return weekDays[dayOfWeek];
  };

  const scheduleColumns = [
    {
      title: '课程代码',
      dataIndex: 'courseCode',
      key: 'courseCode',
      width: 120,
    },
    {
      title: '课程名称',
      dataIndex: 'courseName',
      key: 'courseName',
      width: 150,
    },
    {
      title: '授课教师',
      dataIndex: 'teacher',
      key: 'teacher',
      width: 120,
    },
    {
      title: '星期',
      dataIndex: 'dayOfWeek',
      key: 'dayOfWeek',
      width: 80,
      render: (day: number) => getWeekDay(day),
    },
    {
      title: '时间',
      key: 'time',
      width: 150,
      render: (record: Schedule) => `${record.startTime}-${record.endTime}`,
    },
    {
      title: '周次',
      dataIndex: 'weeks',
      key: 'weeks',
      width: 100,
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

  if (!classroom) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>教室不存在</Title>
        <Button onClick={() => navigate('/classrooms/list')}>
          返回教室列表
        </Button>
      </div>
    );
  }

  // 计算使用率
  const utilizationRate = (schedules.length / 35) * 100; // 假设一周35个时间段

  return (
    <div className="classroom-detail-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/classrooms/list')}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            <Space>
              <HomeOutlined />
              {classroom.name}
            </Space>
          </Title>
          <Badge
            status={classroom.isAvailable ? 'success' : 'error'}
            text={classroom.isAvailable ? '可用' : '不可用'}
          />
        </Space>
        <Space>
          <Button 
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/classrooms/${id}/edit`)}
          >
            编辑教室
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="教室容量"
              value={classroom.capacity}
              suffix="人"
              prefix={<HomeOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="使用率"
              value={utilizationRate}
              precision={1}
              suffix="%"
              prefix={<BarChartOutlined />}
              valueStyle={{ color: utilizationRate > 70 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="设备数量"
              value={classroom.equipment.length}
              suffix="项"
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本周课程"
              value={schedules.length}
              suffix="门"
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Tabs defaultActiveKey="basic">
          <TabPane 
            tab={
              <span>
                <HomeOutlined />
                基本信息
              </span>
            } 
            key="basic"
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="教室名称">{classroom.name}</Descriptions.Item>
              <Descriptions.Item label="所在楼栋">{classroom.building}</Descriptions.Item>
              <Descriptions.Item label="楼层">{classroom.floor}楼</Descriptions.Item>
              <Descriptions.Item label="教室类型">
                <Tag color={getTypeColor(classroom.type)}>
                  {getTypeText(classroom.type)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="容量">{classroom.capacity}人</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Badge
                  status={classroom.isAvailable ? 'success' : 'error'}
                  text={classroom.isAvailable ? '可用' : '不可用'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="设备配置" span={2}>
                <Space wrap>
                  {classroom.equipment.map(item => (
                    <Tag key={item} color="blue">{item}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="教室描述" span={2}>
                {classroom.description || '暂无描述'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <CalendarOutlined />
                课程安排 ({schedules.length})
              </span>
            } 
            key="schedules"
          >
            <Table
              columns={scheduleColumns}
              dataSource={schedules}
              rowKey="id"
              pagination={{
                total: schedules.length,
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 门课程`,
              }}
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BarChartOutlined />
                使用统计
              </span>
            } 
            key="statistics"
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Descriptions bordered column={1}>
                  <Descriptions.Item label="周使用率">
                    {utilizationRate.toFixed(1)}%
                  </Descriptions.Item>
                  <Descriptions.Item label="使用状态">
                    {utilizationRate > 80 ? '使用频繁' : utilizationRate > 50 ? '使用正常' : '使用较少'}
                  </Descriptions.Item>
                  <Descriptions.Item label="空闲时段">
                    {35 - schedules.length} 个
                  </Descriptions.Item>
                  <Descriptions.Item label="维护状态">
                    正常
                  </Descriptions.Item>
                </Descriptions>
              </Col>
              <Col span={12}>
                <Card title="使用建议" size="small">
                  <ul style={{ paddingLeft: '20px', margin: 0 }}>
                    {utilizationRate > 80 && (
                      <li>使用率较高，建议合理安排课程时间</li>
                    )}
                    {utilizationRate < 30 && (
                      <li>使用率较低，可考虑增加课程安排</li>
                    )}
                    <li>定期检查设备状态，确保正常使用</li>
                    <li>保持教室清洁，营造良好学习环境</li>
                  </ul>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ClassroomDetailPage;

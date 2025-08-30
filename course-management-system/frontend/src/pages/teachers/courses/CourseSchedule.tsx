import React, { useState, useEffect } from 'react';
import {
  Card,
  Calendar,
  Badge,
  Select,
  Row,
  Col,
  Typography,
  Space,
  Button,
  Modal,
  Descriptions,
  Tag,
  Table,
  Tabs,
  Alert,
  Empty,
} from 'antd';
import {
  CalendarOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  BookOutlined,
  PrinterOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { scheduleApi, courseApi } from '../../../services/api';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

interface ScheduleItem {
  id: number;
  course: {
    id: number;
    name: string;
    code: string;
    credits: number;
  };
  classroom: {
    id: number;
    name: string;
    building: string;
    capacity: number;
  };
  day_of_week: number;
  start_time: string;
  end_time: string;
  weeks: string;
  semester: string;
  status: 'active' | 'cancelled' | 'rescheduled' | 'suspended';
  created_at: string;
}

interface Course {
  id: number;
  name: string;
  code: string;
  semester: string;
}

const CourseSchedule: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [schedules, setSchedules] = useState<ScheduleItem[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedSemester, setSelectedSemester] = useState('2024-2025-1');
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleItem | null>(null);
  const [viewMode, setViewMode] = useState<'calendar' | 'table'>('calendar');

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    fetchSchedules();
  }, [selectedCourse, selectedSemester]);

  const fetchCourses = async () => {
    try {
      const response = await courseApi.getTeacherCourses();
      setCourses(response.data);
    } catch (error) {
      console.error('获取课程列表失败:', error);
    }
  };

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const params = {
        course_id: selectedCourse,
        semester: selectedSemester,
      };
      const response = await scheduleApi.getTeacherSchedules(params);
      setSchedules(response.data);
    } catch (error) {
      console.error('获取课程表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSchedulesForDate = (date: Dayjs) => {
    const dayOfWeek = date.day() === 0 ? 7 : date.day(); // 转换为1-7格式
    return schedules.filter(schedule => 
      schedule.day_of_week === dayOfWeek &&
      schedule.status === 'active'
    );
  };

  const dateCellRender = (date: Dayjs) => {
    const daySchedules = getSchedulesForDate(date);
    
    if (daySchedules.length === 0) return null;

    return (
      <div style={{ fontSize: '12px' }}>
        {daySchedules.map(schedule => (
          <div key={schedule.id} style={{ marginBottom: '2px' }}>
            <Badge
              status="processing"
              text={
                <span
                  style={{ cursor: 'pointer' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSchedule(schedule);
                    setDetailVisible(true);
                  }}
                >
                  {schedule.start_time.slice(0, 5)} {schedule.course.name}
                </span>
              }
            />
          </div>
        ))}
      </div>
    );
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      'active': 'success',
      'cancelled': 'error',
      'rescheduled': 'warning',
      'suspended': 'default',
    };
    return colorMap[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
      'active': '正常',
      'cancelled': '取消',
      'rescheduled': '调课',
      'suspended': '暂停',
    };
    return textMap[status] || status;
  };

  const getDayName = (dayOfWeek: number) => {
    const dayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return dayNames[dayOfWeek] || '';
  };

  const tableColumns = [
    {
      title: '时间',
      key: 'time',
      render: (_: any, record: ScheduleItem) => (
        <div>
          <div>{getDayName(record.day_of_week)}</div>
          <Text type="secondary">
            {record.start_time} - {record.end_time}
          </Text>
        </div>
      ),
    },
    {
      title: '课程',
      key: 'course',
      render: (_: any, record: ScheduleItem) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.course.name}</div>
          <Text type="secondary">{record.course.code}</Text>
        </div>
      ),
    },
    {
      title: '教室',
      key: 'classroom',
      render: (_: any, record: ScheduleItem) => (
        <div>
          <div>{record.classroom.name}</div>
          <Text type="secondary">{record.classroom.building}</Text>
        </div>
      ),
    },
    {
      title: '周次',
      dataIndex: 'weeks',
      key: 'weeks',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: ScheduleItem) => (
        <Button
          type="link"
          onClick={() => {
            setSelectedSchedule(record);
            setDetailVisible(true);
          }}
        >
          查看详情
        </Button>
      ),
    },
  ];

  const generateWeeklySchedule = () => {
    const weekDays = [1, 2, 3, 4, 5, 6, 7]; // 周一到周日
    const timeSlots = [
      '08:00-09:40',
      '10:00-11:40',
      '14:00-15:40',
      '16:00-17:40',
      '19:00-20:40',
    ];

    return (
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #d9d9d9', padding: '8px', background: '#fafafa' }}>
                时间
              </th>
              {weekDays.map(day => (
                <th
                  key={day}
                  style={{ border: '1px solid #d9d9d9', padding: '8px', background: '#fafafa' }}
                >
                  {getDayName(day)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {timeSlots.map(timeSlot => (
              <tr key={timeSlot}>
                <td style={{ border: '1px solid #d9d9d9', padding: '8px', background: '#fafafa' }}>
                  {timeSlot}
                </td>
                {weekDays.map(day => {
                  const daySchedules = schedules.filter(schedule => 
                    schedule.day_of_week === day &&
                    schedule.start_time.slice(0, 5) === timeSlot.split('-')[0]
                  );
                  
                  return (
                    <td
                      key={`${day}-${timeSlot}`}
                      style={{ 
                        border: '1px solid #d9d9d9', 
                        padding: '8px',
                        minHeight: '60px',
                        verticalAlign: 'top'
                      }}
                    >
                      {daySchedules.map(schedule => (
                        <div
                          key={schedule.id}
                          style={{
                            background: '#e6f7ff',
                            border: '1px solid #91d5ff',
                            borderRadius: '4px',
                            padding: '4px',
                            marginBottom: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                          }}
                          onClick={() => {
                            setSelectedSchedule(schedule);
                            setDetailVisible(true);
                          }}
                        >
                          <div style={{ fontWeight: 'bold' }}>
                            {schedule.course.name}
                          </div>
                          <div>{schedule.classroom.name}</div>
                          <div>第{schedule.weeks}周</div>
                        </div>
                      ))}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>课程表</Title>
        
        <Row gutter={16} style={{ marginBottom: '16px' }}>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="选择课程"
              style={{ width: '100%' }}
              value={selectedCourse}
              onChange={setSelectedCourse}
              allowClear
            >
              <Option value={null}>全部课程</Option>
              {courses.map(course => (
                <Option key={course.id} value={course.id}>
                  {course.name}
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="选择学期"
              style={{ width: '100%' }}
              value={selectedSemester}
              onChange={setSelectedSemester}
            >
              <Option value="2024-2025-1">2024-2025学年第一学期</Option>
              <Option value="2024-2025-2">2024-2025学年第二学期</Option>
            </Select>
          </Col>
          
          <Col xs={24} sm={8} md={12}>
            <Space>
              <Button
                type={viewMode === 'calendar' ? 'primary' : 'default'}
                icon={<CalendarOutlined />}
                onClick={() => setViewMode('calendar')}
              >
                日历视图
              </Button>
              <Button
                type={viewMode === 'table' ? 'primary' : 'default'}
                onClick={() => setViewMode('table')}
              >
                列表视图
              </Button>
              <Button icon={<PrinterOutlined />}>
                打印
              </Button>
              <Button icon={<DownloadOutlined />}>
                导出
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {schedules.length === 0 ? (
        <Card>
          <Empty
            description="暂无课程安排"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      ) : (
        <Card loading={loading}>
          <Tabs activeKey={viewMode} onChange={(key) => setViewMode(key as any)}>
            <TabPane tab="日历视图" key="calendar">
              <Calendar
                dateCellRender={dateCellRender}
                value={selectedDate}
                onSelect={setSelectedDate}
              />
            </TabPane>
            
            <TabPane tab="周视图" key="week">
              {generateWeeklySchedule()}
            </TabPane>
            
            <TabPane tab="列表视图" key="table">
              <Table
                columns={tableColumns}
                dataSource={schedules}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                }}
              />
            </TabPane>
          </Tabs>
        </Card>
      )}

      {/* 课程详情弹窗 */}
      <Modal
        title="课程安排详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedSchedule && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="课程名称" span={2}>
              <Space>
                <BookOutlined />
                {selectedSchedule.course.name}
                <Tag>{selectedSchedule.course.code}</Tag>
              </Space>
            </Descriptions.Item>
            
            <Descriptions.Item label="上课时间">
              <Space>
                <ClockCircleOutlined />
                {getDayName(selectedSchedule.day_of_week)} {selectedSchedule.start_time} - {selectedSchedule.end_time}
              </Space>
            </Descriptions.Item>
            
            <Descriptions.Item label="教室">
              <Space>
                <EnvironmentOutlined />
                {selectedSchedule.classroom.building} {selectedSchedule.classroom.name}
              </Space>
            </Descriptions.Item>
            
            <Descriptions.Item label="周次">
              第{selectedSchedule.weeks}周
            </Descriptions.Item>
            
            <Descriptions.Item label="容量">
              <Space>
                <TeamOutlined />
                {selectedSchedule.classroom.capacity}人
              </Space>
            </Descriptions.Item>
            
            <Descriptions.Item label="学分">
              {selectedSchedule.course.credits}学分
            </Descriptions.Item>
            
            <Descriptions.Item label="状态">
              <Tag color={getStatusColor(selectedSchedule.status)}>
                {getStatusText(selectedSchedule.status)}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default CourseSchedule;

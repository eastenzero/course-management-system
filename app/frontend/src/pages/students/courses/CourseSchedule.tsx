import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Select,
  Button,
  Space,
  Typography,
  Tag,
  Tooltip,
  Empty,
  Spin,
  message,
  Row,
  Col
} from 'antd';
import {
  CalendarOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  UserOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { studentAPI } from '../../../services/studentAPI';
import { scheduleAPI } from '../../../api/schedules';
import { useAppSelector } from '../../../store';

const { Option } = Select;
const { Title, Text } = Typography;

interface TimeSlot {
  id: number;
  name: string;
  start_time: string;
  end_time: string;
  order: number;
}

interface ScheduleItem {
  course_id: number;
  course_name: string;
  course_code: string;
  teacher_name: string;
  classroom: string;
  classroom_id: number;
  time_slot: string;
  time_slot_id: number;
  day_of_week: number;
  day_of_week_display: string;
  start_time: string;
  end_time: string;
  week_range: string;
  semester: string;
  grid_key: string;
}

const CourseSchedule: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('2024春');
  const [selectedWeek, setSelectedWeek] = useState<string>('');
  const [exporting, setExporting] = useState(false);

  const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

  useEffect(() => {
    fetchTimeSlots();
  }, []);

  useEffect(() => {
    if (user?.id) {
      fetchSchedule();
    }
  }, [selectedSemester, selectedWeek, user?.id]);

  const fetchTimeSlots = async () => {
    try {
      const response = await scheduleAPI.getTimeSlots();
      if (response.data?.data) {
        setTimeSlots(response.data.data);
      } else {
        setTimeSlots(response.data || []);
      }
    } catch (error: any) {
      console.error('获取时间段失败:', error);
      message.error('获取时间段失败');
      // 退回到硬编码时间段
      setTimeSlots([
        { id: 1, name: '第1节', start_time: '08:00', end_time: '09:40', order: 1 },
        { id: 2, name: '第2节', start_time: '10:00', end_time: '11:40', order: 2 },
        { id: 3, name: '第3节', start_time: '14:00', end_time: '15:40', order: 3 },
        { id: 4, name: '第4节', start_time: '16:00', end_time: '17:40', order: 4 },
        { id: 5, name: '第5节', start_time: '19:00', end_time: '20:40', order: 5 }
      ]);
    }
  };

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const params: any = {
        user_type: 'student',
        user_id: user?.id || ''
      };
      if (selectedSemester) params.semester = selectedSemester;
      if (selectedWeek) params.week = selectedWeek;
      
      const response = await studentAPI.getSchedule(params);
      
      // 转换后端数据格式为前端需要的格式
      if (response.data?.data?.schedule_table) {
        const scheduleTable = response.data.data.schedule_table;
        const timeSlotsData = response.data.data.time_slots || timeSlots;
        
        // 将表格数据转换为课程列表
        const scheduleItems: ScheduleItem[] = [];
        
        // 遍历每一天（1-7表示周一到周日）
        for (let day = 1; day <= 7; day++) {
          const daySchedule = scheduleTable[day];
          if (daySchedule) {
            // 遍历每个时间段
            for (const timeSlotId in daySchedule) {
              const courseData = daySchedule[timeSlotId];
              if (courseData) {
                const timeSlot = timeSlotsData.find((ts: any) => ts.id === parseInt(timeSlotId));
                
                scheduleItems.push({
                  course_id: courseData.id,
                  course_name: courseData.course_name,
                  course_code: courseData.course_code,
                  teacher_name: courseData.teacher_name,
                  classroom: courseData.classroom,
                  classroom_id: 0, // 默认值，后端没有返回这个字段
                  time_slot: timeSlot?.name || `第${timeSlotId}节`,
                  time_slot_id: parseInt(timeSlotId),
                  day_of_week: day,
                  day_of_week_display: weekDays[day - 1],
                  start_time: timeSlot?.start_time || '',
                  end_time: timeSlot?.end_time || '',
                  week_range: courseData.week_range,
                  semester: selectedSemester,
                  grid_key: `${day}-${timeSlotId}`
                });
              }
            }
          }
        }
        
        setSchedule(scheduleItems);
      } else {
        // 如果已经是数组格式，直接使用
        setSchedule(response.data || []);
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取课程表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExportSchedule = async () => {
    try {
      setExporting(true);
      const params: any = {};
      if (selectedSemester) params.semester = selectedSemester;
      
      const response = await studentAPI.exportSchedule(params);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `课程表_${selectedSemester || '全部'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('课程表导出成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '导出课程表失败');
    } finally {
      setExporting(false);
    }
  };

  // 构建课程表网格数据
  const buildScheduleGrid = () => {
    const grid: Record<number, Record<number, ScheduleItem | null>> = {};
    
    // 初始化网格
    timeSlots.forEach(timeSlot => {
      grid[timeSlot.id] = {};
      weekDays.forEach((_, dayIndex) => {
        grid[timeSlot.id][dayIndex + 1] = null; // day_of_week 从1开始
      });
    });

    // 填充课程数据
    schedule.forEach(item => {
      if (grid[item.time_slot_id] && !grid[item.time_slot_id][item.day_of_week]) {
        grid[item.time_slot_id][item.day_of_week] = item;
      }
    });

    return grid;
  };

  const scheduleGrid = buildScheduleGrid();

  const renderCourseCell = (course: ScheduleItem | null) => {
    if (!course) {
      return <div style={{ height: '80px', padding: '8px' }}></div>;
    }

    return (
      <div
        style={{
          height: '80px',
          padding: '8px',
          backgroundColor: '#e6f7ff',
          border: '1px solid #91d5ff',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        <Tooltip
          title={
            <div>
              <div><strong>{course.course_name}</strong></div>
              <div>课程代码：{course.course_code}</div>
              <div>授课教师：{course.teacher_name}</div>
              <div>教室：{course.classroom}</div>
              <div>周次：{course.week_range}</div>
            </div>
          }
        >
          <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px' }}>
            {course.course_name}
          </div>
          <div style={{ fontSize: '10px', color: '#666' }}>
            <EnvironmentOutlined /> {course.classroom}
          </div>
          <div style={{ fontSize: '10px', color: '#666' }}>
            <UserOutlined /> {course.teacher_name}
          </div>
        </Tooltip>
      </div>
    );
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2}>课程表</Title>
        <Space>
          <Select
            placeholder="选择学期"
            style={{ width: 200 }}
            value={selectedSemester}
            onChange={setSelectedSemester}
            allowClear
          >
            <Option value="2024春">2024春季学期</Option>
            <Option value="2024秋">2024秋季学期</Option>
            <Option value="2025春">2025春季学期</Option>
          </Select>
          <Select
            placeholder="选择周次"
            style={{ width: 120 }}
            value={selectedWeek}
            onChange={setSelectedWeek}
            allowClear
          >
            {Array.from({ length: 20 }, (_, i) => (
              <Option key={i + 1} value={`${i + 1}`}>第{i + 1}周</Option>
            ))}
          </Select>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={handleExportSchedule}
          >
            导出课程表
          </Button>
        </Space>
      </div>

      {schedule.length === 0 ? (
        <Card>
          <Empty
            description="暂无课程安排"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      ) : (
        <Card>
          {/* 课程表网格 */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', minWidth: '800px', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ 
                    width: '100px', 
                    padding: '12px', 
                    backgroundColor: '#fafafa', 
                    border: '1px solid #d9d9d9',
                    textAlign: 'center'
                  }}>
                    时间
                  </th>
                  {weekDays.map((day, index) => (
                    <th
                      key={index}
                      style={{
                        padding: '12px',
                        backgroundColor: '#fafafa',
                        border: '1px solid #d9d9d9',
                        textAlign: 'center',
                        minWidth: '120px'
                      }}
                    >
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {timeSlots.map((timeSlot) => (
                  <tr key={timeSlot.id}>
                    <td style={{
                      padding: '8px',
                      backgroundColor: '#fafafa',
                      border: '1px solid #d9d9d9',
                      textAlign: 'center',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}>
                      <div>{timeSlot.name}</div>
                      <div style={{ fontSize: '10px', color: '#999' }}>
                        {timeSlot.start_time}-{timeSlot.end_time}
                      </div>
                    </td>
                    {weekDays.map((_, dayIndex) => (
                      <td
                        key={dayIndex}
                        style={{
                          padding: '4px',
                          border: '1px solid #d9d9d9',
                          verticalAlign: 'top'
                        }}
                      >
                        {renderCourseCell(scheduleGrid[timeSlot.id]?.[dayIndex + 1] || null)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 课程列表视图 */}
          <div style={{ marginTop: '24px' }}>
            <Title level={4}>课程列表</Title>
            <Row gutter={[16, 16]}>
              {schedule.map((course, index) => (
                <Col xs={24} sm={12} lg={8} key={index}>
                  <Card size="small">
                    <div style={{ marginBottom: '8px' }}>
                      <Text strong>{course.course_name}</Text>
                      <Tag style={{ marginLeft: '8px' }}>{course.course_code}</Tag>
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      <div style={{ marginBottom: '4px' }}>
                        <CalendarOutlined /> {weekDays[course.day_of_week - 1]}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <ClockCircleOutlined /> {course.start_time}-{course.end_time}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <EnvironmentOutlined /> {course.classroom}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <UserOutlined /> {course.teacher_name}
                      </div>
                      <div>
                        周次：{course.week_range}
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CourseSchedule;

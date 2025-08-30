import React, { useState } from 'react';
import { Card, Tabs, Space, Typography, Tag, Button, Collapse } from 'antd';
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  UserOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import '../../styles/mobile.css';

const { Text, Title } = Typography;
const { TabPane } = Tabs;
const { Panel } = Collapse;

interface ScheduleItem {
  id: number;
  course: {
    id: number;
    name: string;
    code: string;
  };
  teacher: {
    id: number;
    name: string;
  };
  classroom: {
    id: number;
    name: string;
    building: string;
  };
  day_of_week: number;
  start_time: string;
  end_time: string;
  week_start: number;
  week_end: number;
}

interface MobileScheduleProps {
  schedules: ScheduleItem[];
  currentWeek?: number;
  onCourseClick?: (courseId: number) => void;
  className?: string;
}

const MobileSchedule: React.FC<MobileScheduleProps> = ({
  schedules,
  currentWeek = 1,
  onCourseClick,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState('0');
  const [viewMode, setViewMode] = useState<'daily' | 'weekly'>('daily');

  const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const timeSlots = [
    '08:00-09:40',
    '10:00-11:40',
    '14:00-15:40',
    '16:00-17:40',
    '19:00-20:40'
  ];

  // 按天分组课程
  const groupSchedulesByDay = () => {
    const grouped: { [key: number]: ScheduleItem[] } = {};
    
    schedules.forEach(schedule => {
      if (schedule.week_start <= currentWeek && schedule.week_end >= currentWeek) {
        if (!grouped[schedule.day_of_week]) {
          grouped[schedule.day_of_week] = [];
        }
        grouped[schedule.day_of_week].push(schedule);
      }
    });

    // 对每天的课程按时间排序
    Object.keys(grouped).forEach(day => {
      grouped[parseInt(day)].sort((a, b) => 
        a.start_time.localeCompare(b.start_time)
      );
    });

    return grouped;
  };

  // 获取今天是周几
  const getTodayIndex = () => {
    return new Date().getDay();
  };

  // 渲染单个课程项
  const renderScheduleItem = (schedule: ScheduleItem) => (
    <Card 
      key={schedule.id}
      className="mobile-schedule-item"
      size="small"
      hoverable
      onClick={() => onCourseClick?.(schedule.course.id)}
      style={{ marginBottom: 8 }}
    >
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={5} style={{ margin: 0, color: '#1890ff' }}>
            {schedule.course.name}
          </Title>
          <Tag size="small">{schedule.course.code}</Tag>
        </div>
        
        <Space size={16}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <ClockCircleOutlined style={{ marginRight: 4, color: '#666' }} />
            <Text style={{ fontSize: 12 }}>
              {schedule.start_time}-{schedule.end_time}
            </Text>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <EnvironmentOutlined style={{ marginRight: 4, color: '#666' }} />
            <Text style={{ fontSize: 12 }}>
              {schedule.classroom.building} {schedule.classroom.name}
            </Text>
          </div>
        </Space>
        
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <UserOutlined style={{ marginRight: 4, color: '#666' }} />
          <Text style={{ fontSize: 12 }}>
            {schedule.teacher.name}
          </Text>
        </div>
        
        <Text type="secondary" style={{ fontSize: 11 }}>
          第{schedule.week_start}-{schedule.week_end}周
        </Text>
      </Space>
    </Card>
  );

  // 渲染每日视图
  const renderDailyView = () => {
    const groupedSchedules = groupSchedulesByDay();
    const todayIndex = getTodayIndex();

    return (
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        size="small"
        tabPosition="top"
      >
        {[1, 2, 3, 4, 5, 6, 0].map((dayIndex, index) => {
          const isToday = dayIndex === todayIndex;
          const daySchedules = groupedSchedules[dayIndex] || [];
          
          return (
            <TabPane 
              tab={
                <span style={{ color: isToday ? '#1890ff' : undefined }}>
                  {dayNames[dayIndex]}
                  {isToday && <span style={{ fontSize: 10 }}> (今天)</span>}
                </span>
              } 
              key={index.toString()}
            >
              <div style={{ padding: '8px 0' }}>
                {daySchedules.length > 0 ? (
                  daySchedules.map(renderScheduleItem)
                ) : (
                  <Card size="small" style={{ textAlign: 'center', color: '#999' }}>
                    <Text type="secondary">今天没有课程安排</Text>
                  </Card>
                )}
              </div>
            </TabPane>
          );
        })}
      </Tabs>
    );
  };

  // 渲染周视图
  const renderWeeklyView = () => {
    const groupedSchedules = groupSchedulesByDay();

    return (
      <Collapse size="small" ghost>
        {[1, 2, 3, 4, 5, 6, 0].map(dayIndex => {
          const daySchedules = groupedSchedules[dayIndex] || [];
          const isToday = dayIndex === getTodayIndex();
          
          return (
            <Panel 
              header={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: isToday ? '#1890ff' : undefined, fontWeight: isToday ? 600 : 400 }}>
                    {dayNames[dayIndex]}
                    {isToday && <span style={{ fontSize: 12, marginLeft: 4 }}>(今天)</span>}
                  </span>
                  <Tag size="small" color={daySchedules.length > 0 ? 'blue' : 'default'}>
                    {daySchedules.length}节课
                  </Tag>
                </div>
              }
              key={dayIndex.toString()}
            >
              {daySchedules.length > 0 ? (
                daySchedules.map(renderScheduleItem)
              ) : (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  没有课程安排
                </Text>
              )}
            </Panel>
          );
        })}
      </Collapse>
    );
  };

  return (
    <div className={`mobile-schedule ${className}`}>
      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              <CalendarOutlined style={{ marginRight: 8 }} />
              第{currentWeek}周课程表
            </span>
            <Space>
              <Button 
                size="small" 
                type={viewMode === 'daily' ? 'primary' : 'default'}
                onClick={() => setViewMode('daily')}
              >
                日视图
              </Button>
              <Button 
                size="small" 
                type={viewMode === 'weekly' ? 'primary' : 'default'}
                onClick={() => setViewMode('weekly')}
              >
                周视图
              </Button>
            </Space>
          </div>
        }
        size="small"
      >
        {viewMode === 'daily' ? renderDailyView() : renderWeeklyView()}
      </Card>
    </div>
  );
};

export default MobileSchedule;

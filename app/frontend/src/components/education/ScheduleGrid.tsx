import React from 'react';
import { Card, Typography, Tooltip, Empty } from 'antd';
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  UserOutlined,
  BookOutlined
} from '@ant-design/icons';

const { Text } = Typography;

export interface ScheduleItem {
  id: string;
  course_id: number;
  course_name: string;
  course_code: string;
  teacher_name?: string;
  classroom?: string;
  time_slot: string;
  day_of_week: number; // 1-7 (周一到周日)
  start_time: string;
  end_time: string;
  week_range?: string;
  color?: string;
}

export interface ScheduleGridProps {
  scheduleData: ScheduleItem[];
  timeSlots?: string[];
  weekDays?: string[];
  onCellClick?: (item: ScheduleItem | null, dayIndex: number, timeSlotIndex: number) => void;
  mode?: 'view' | 'edit';
  showWeekend?: boolean;
  cellHeight?: number;
  className?: string;
  style?: React.CSSProperties;
}

const ScheduleGrid: React.FC<ScheduleGridProps> = ({
  scheduleData,
  timeSlots = [
    '08:00-10:00',
    '10:10-12:10',
    '14:00-16:00',
    '16:10-18:10',
    '19:00-21:00'
  ],
  weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  onCellClick,
  mode = 'view',
  showWeekend = false,
  cellHeight = 80,
  className,
  style
}) => {
  const displayWeekDays = showWeekend ? weekDays : weekDays.slice(0, 5);

  // 构建课程表网格数据
  const buildScheduleGrid = () => {
    const grid: Record<string, Record<number, ScheduleItem | null>> = {};
    
    // 初始化网格
    timeSlots.forEach(timeSlot => {
      grid[timeSlot] = {};
      displayWeekDays.forEach((_, dayIndex) => {
        grid[timeSlot][dayIndex] = null;
      });
    });

    // 填充课程数据
    scheduleData.forEach(item => {
      const timeSlot = `${item.start_time}-${item.end_time}`;
      const dayIndex = item.day_of_week - 1; // 转换为0-6的索引
      
      if (grid[timeSlot] && dayIndex >= 0 && dayIndex < displayWeekDays.length) {
        grid[timeSlot][dayIndex] = item;
      }
    });

    return grid;
  };

  const scheduleGrid = buildScheduleGrid();

  const renderCourseCell = (
    course: ScheduleItem | null, 
    dayIndex: number, 
    timeSlotIndex: number
  ) => {
    const cellStyle: React.CSSProperties = {
      height: `${cellHeight}px`,
      padding: '8px',
      cursor: mode === 'edit' || onCellClick ? 'pointer' : 'default',
      border: '1px solid #d9d9d9',
      borderRadius: '4px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden'
    };

    if (!course) {
      return (
        <div
          style={{
            ...cellStyle,
            backgroundColor: '#fafafa'
          }}
          onClick={() => onCellClick?.(null, dayIndex, timeSlotIndex)}
        />
      );
    }

    const courseStyle: React.CSSProperties = {
      ...cellStyle,
      backgroundColor: course.color || '#e6f7ff',
      borderColor: course.color || '#91d5ff',
      borderWidth: '2px'
    };

    const content = (
      <div style={courseStyle} onClick={() => onCellClick?.(course, dayIndex, timeSlotIndex)}>
        <div style={{ 
          fontSize: '12px', 
          fontWeight: 'bold', 
          marginBottom: '4px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {course.course_name}
        </div>
        
        <div style={{ 
          fontSize: '10px', 
          color: '#666',
          display: 'flex',
          alignItems: 'center',
          marginBottom: '2px'
        }}>
          <EnvironmentOutlined style={{ marginRight: '2px' }} />
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {course.classroom || '待安排'}
          </span>
        </div>
        
        {course.teacher_name && (
          <div style={{ 
            fontSize: '10px', 
            color: '#666',
            display: 'flex',
            alignItems: 'center'
          }}>
            <UserOutlined style={{ marginRight: '2px' }} />
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {course.teacher_name}
            </span>
          </div>
        )}
      </div>
    );

    if (mode === 'view') {
      return (
        <Tooltip
          title={
            <div>
              <div><strong>{course.course_name}</strong></div>
              <div>课程代码：{course.course_code}</div>
              {course.teacher_name && <div>授课教师：{course.teacher_name}</div>}
              {course.classroom && <div>教室：{course.classroom}</div>}
              {course.week_range && <div>周次：{course.week_range}</div>}
              <div>时间：{course.start_time}-{course.end_time}</div>
            </div>
          }
          placement="top"
        >
          {content}
        </Tooltip>
      );
    }

    return content;
  };

  if (scheduleData.length === 0) {
    return (
      <Card className={className} style={style}>
        <Empty
          description="暂无课程安排"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  return (
    <Card className={className} style={style}>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ 
          width: '100%', 
          minWidth: showWeekend ? '900px' : '700px', 
          borderCollapse: 'collapse' 
        }}>
          <thead>
            <tr>
              <th style={{ 
                width: '100px', 
                padding: '12px', 
                backgroundColor: '#fafafa', 
                border: '1px solid #d9d9d9',
                textAlign: 'center',
                fontWeight: 'bold'
              }}>
                <ClockCircleOutlined style={{ marginRight: '4px' }} />
                时间
              </th>
              {displayWeekDays.map((day, index) => (
                <th
                  key={index}
                  style={{
                    padding: '12px',
                    backgroundColor: '#fafafa',
                    border: '1px solid #d9d9d9',
                    textAlign: 'center',
                    minWidth: '120px',
                    fontWeight: 'bold'
                  }}
                >
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {timeSlots.map((timeSlot, timeIndex) => (
              <tr key={timeIndex}>
                <td style={{
                  padding: '8px',
                  backgroundColor: '#fafafa',
                  border: '1px solid #d9d9d9',
                  textAlign: 'center',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  verticalAlign: 'middle'
                }}>
                  {timeSlot}
                </td>
                {displayWeekDays.map((_, dayIndex) => (
                  <td
                    key={dayIndex}
                    style={{
                      padding: '4px',
                      border: '1px solid #d9d9d9',
                      verticalAlign: 'top'
                    }}
                  >
                    {renderCourseCell(
                      scheduleGrid[timeSlot]?.[dayIndex] || null,
                      dayIndex,
                      timeIndex
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* 图例 */}
      {mode === 'view' && (
        <div style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: '#fafafa',
          borderRadius: '4px'
        }}>
          <Text style={{ fontSize: '12px', color: '#666' }}>
            <BookOutlined style={{ marginRight: '4px' }} />
            点击课程单元格查看详细信息
          </Text>
        </div>
      )}
    </Card>
  );
};

export default ScheduleGrid;

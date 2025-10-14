import React, { useMemo } from 'react';
import { Card, Tag, Tooltip, Empty } from 'antd';
import {
  ClockCircleOutlined,
  UserOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import type { Schedule, TimeSlot } from '../../types/index';
import './ScheduleGrid.css';

interface ScheduleGridProps {
  schedules: Schedule[];
  timeSlots: TimeSlot[];
  weekDays: string[];
  selectedWeek?: number;
  onCellClick?: (day: number, timeSlot: number) => void;
  onScheduleClick?: (schedule: Schedule) => void;
  editable?: boolean;
  showTeacher?: boolean;
  showClassroom?: boolean;
  compact?: boolean;
}

interface ScheduleCellProps {
  schedule?: Schedule;
  day: number;
  timeSlot: number;
  onClick?: (day: number, timeSlot: number) => void;
  onScheduleClick?: (schedule: Schedule) => void;
  editable?: boolean;
  showTeacher?: boolean;
  showClassroom?: boolean;
  compact?: boolean;
}

const ScheduleCell: React.FC<ScheduleCellProps> = ({
  schedule,
  day,
  timeSlot,
  onClick,
  onScheduleClick,
  editable = false,
  showTeacher = true,
  showClassroom = true,
  compact = false,
}) => {
  const handleClick = () => {
    if (schedule && onScheduleClick) {
      onScheduleClick(schedule);
    } else if (editable && onClick) {
      onClick(day, timeSlot);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return '#1890ff';
      case 'in_progress':
        return '#52c41a';
      case 'completed':
        return '#8c8c8c';
      case 'cancelled':
        return '#f5222d';
      default:
        return '#d9d9d9';
    }
  };

  if (!schedule) {
    return (
      <div
        className={`schedule-cell empty ${editable ? 'editable' : ''}`}
        onClick={handleClick}
      >
        {editable && <div className="add-indicator">+</div>}
      </div>
    );
  }

  return (
    <Tooltip
      title={
        <div>
          <div>
            <strong>{schedule.course.name}</strong>
          </div>
          <div>课程代码: {schedule.course.code}</div>
          {showTeacher && (
            <div>
              教师: {schedule.teacher.first_name} {schedule.teacher.last_name}
            </div>
          )}
          {showClassroom && <div>教室: {schedule.classroom.name}</div>}
          <div>学分: {schedule.course.credits}</div>
          <div>状态: {schedule.status}</div>
        </div>
      }
      placement="top"
    >
      <div
        className={`schedule-cell filled ${compact ? 'compact' : ''} ${editable ? 'editable' : ''}`}
        onClick={handleClick}
        style={{ borderLeftColor: getStatusColor(schedule.status) }}
      >
        <div className="course-info">
          <div className="course-name" title={schedule.course.name}>
            {schedule.course.name}
          </div>
          <div className="course-code">{schedule.course.code}</div>
        </div>

        {!compact && (
          <div className="schedule-details">
            {showTeacher && (
              <div className="detail-item">
                <UserOutlined />
                <span>
                  {schedule.teacher.first_name} {schedule.teacher.last_name}
                </span>
              </div>
            )}
            {showClassroom && (
              <div className="detail-item">
                <HomeOutlined />
                <span>{schedule.classroom.name}</span>
              </div>
            )}
          </div>
        )}

        <div className="schedule-status">
          <Tag color={getStatusColor(schedule.status)}>{schedule.status}</Tag>
        </div>
      </div>
    </Tooltip>
  );
};

const ScheduleGrid: React.FC<ScheduleGridProps> = ({
  schedules,
  timeSlots,
  weekDays,
  selectedWeek = 1,
  onCellClick,
  onScheduleClick,
  editable = false,
  showTeacher = true,
  showClassroom = true,
  compact = false,
}) => {
  // 根据周次过滤课程表
  const filteredSchedules = useMemo(() => {
    return schedules.filter(schedule => schedule.week_number === selectedWeek);
  }, [schedules, selectedWeek]);

  // 创建课程表矩阵
  const scheduleMatrix = useMemo(() => {
    const matrix: (Schedule | undefined)[][] = Array(weekDays.length)
      .fill(null)
      .map(() => Array(timeSlots.length).fill(undefined));

    filteredSchedules.forEach(schedule => {
      const dayIndex =
        schedule.day_of_week === 0 ? 6 : schedule.day_of_week - 1; // 转换为0-6，周一为0
      const timeIndex = timeSlots.findIndex(
        slot => slot.id === schedule.time_slot.id
      );

      if (dayIndex >= 0 && dayIndex < weekDays.length && timeIndex >= 0) {
        matrix[dayIndex][timeIndex] = schedule;
      }
    });

    return matrix;
  }, [filteredSchedules, weekDays.length, timeSlots]);

  if (timeSlots.length === 0) {
    return (
      <Card>
        <Empty description="暂无时间段配置" />
      </Card>
    );
  }

  return (
    <Card className="schedule-grid-card">
      <div className="schedule-grid">
        {/* 时间表头 */}
        <div className="time-header">
          <div className="corner-cell"></div>
          {timeSlots.map(slot => (
            <div key={slot.id} className="time-slot-header">
              <div className="slot-name">{slot.name}</div>
              <div className="slot-time">
                <ClockCircleOutlined />
                <span>
                  {slot.start_time}-{slot.end_time}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 课程表主体 */}
        <div className="schedule-body">
          {weekDays.map((day, dayIndex) => (
            <div key={day} className="day-row">
              <div className="day-header">
                <div className="day-name">{day}</div>
                <div className="day-date">{/* 这里可以添加具体日期 */}</div>
              </div>

              <div className="day-cells">
                {timeSlots.map((_, slotIndex) => (
                  <ScheduleCell
                    key={`${dayIndex}-${slotIndex}`}
                    schedule={scheduleMatrix[dayIndex][slotIndex]}
                    day={dayIndex}
                    timeSlot={slotIndex}
                    onClick={onCellClick}
                    onScheduleClick={onScheduleClick}
                    editable={editable}
                    showTeacher={showTeacher}
                    showClassroom={showClassroom}
                    compact={compact}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default ScheduleGrid;

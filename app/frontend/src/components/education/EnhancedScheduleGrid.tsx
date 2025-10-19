import React, { useState, useCallback, useMemo } from 'react';
import { Card, Typography, Tooltip, Tag, Empty, Button, Select, Slider, Switch } from 'antd';
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  UserOutlined,
  BookOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  ExpandOutlined,
  CompressOutlined,
  CalendarOutlined,
  TableOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
// import { DndProvider, useDrag, useDrop } from 'react-dnd';
// import { HTML5Backend } from 'react-dnd-html5-backend';

const { Text } = Typography;
const { Option } = Select;

export interface ScheduleItem {
  id: string;
  course_id: number;
  course_name: string;
  course_code: string;
  teacher_name?: string;
  classroom?: string;
  time_slot: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  week_range?: string;
  color?: string;
  duration?: number; // 课程时长（节数）
}

export interface EnhancedScheduleGridProps {
  scheduleData: ScheduleItem[];
  timeSlots?: string[];
  weekDays?: string[];
  onCellClick?: (item: ScheduleItem | null, dayIndex: number, timeSlotIndex: number) => void;
  onItemMove?: (item: ScheduleItem, newDay: number, newTimeSlot: number) => void;
  mode?: 'view' | 'edit';
  showWeekend?: boolean;
  enableDragDrop?: boolean;
  enableZoom?: boolean;
  enableMultiView?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

type ViewMode = 'grid' | 'list' | 'calendar';

const DraggableCourseCell: React.FC<{
  course: ScheduleItem;
  dayIndex: number;
  timeSlotIndex: number;
  cellHeight: number;
  onCellClick?: (item: ScheduleItem, dayIndex: number, timeSlotIndex: number) => void;
  enableDrag: boolean;
}> = ({ course, dayIndex, timeSlotIndex, cellHeight, onCellClick, enableDrag }) => {
  // const [{ isDragging }, drag] = useDrag({
  //   type: 'course',
  //   item: { course, dayIndex, timeSlotIndex },
  //   canDrag: enableDrag,
  //   collect: (monitor) => ({
  //     isDragging: monitor.isDragging(),
  //   }),
  // });
  const isDragging = false;
  const drag = undefined;

  const cellStyle: React.CSSProperties = {
    height: `${cellHeight}px`,
    padding: '8px',
    cursor: enableDrag ? 'move' : 'pointer',
    border: '2px solid',
    borderColor: course.color || '#91d5ff',
    borderRadius: '6px',
    backgroundColor: course.color || '#e6f7ff',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    position: 'relative',
    overflow: 'hidden',
    opacity: isDragging ? 0.5 : 1,
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  const content = (
    <div 
      ref={enableDrag ? drag : undefined}
      style={cellStyle} 
      onClick={() => onCellClick?.(course, dayIndex, timeSlotIndex)}
    >
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
      
      {enableDrag && (
        <div style={{
          position: 'absolute',
          top: '2px',
          right: '2px',
          fontSize: '8px',
          color: '#999'
        }}>
          ⋮⋮
        </div>
      )}
    </div>
  );

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
};

const DroppableCell: React.FC<{
  dayIndex: number;
  timeSlotIndex: number;
  cellHeight: number;
  onDrop: (item: any, dayIndex: number, timeSlotIndex: number) => void;
  children?: React.ReactNode;
}> = ({ dayIndex: _dayIndex, timeSlotIndex: _timeSlotIndex, cellHeight, onDrop: _onDrop, children }) => {
  // const [{ isOver }, drop] = useDrop({
  //   accept: 'course',
  //   drop: (item: any) => onDrop(item, dayIndex, timeSlotIndex),
  //   collect: (monitor) => ({
  //     isOver: monitor.isOver(),
  //   }),
  // });
  const isOver = false;
  const drop = undefined;

  const cellStyle: React.CSSProperties = {
    height: `${cellHeight}px`,
    padding: '4px',
    border: '1px solid #d9d9d9',
    verticalAlign: 'top',
    backgroundColor: isOver ? '#f0f8ff' : 'transparent',
    transition: 'background-color 0.2s ease',
  };

  return (
    <td ref={drop} style={cellStyle}>
      {children}
    </td>
  );
};

const EnhancedScheduleGrid: React.FC<EnhancedScheduleGridProps> = ({
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
  onItemMove,
  mode = 'view',
  showWeekend = false,
  enableDragDrop = false,
  enableZoom = true,
  enableMultiView = true,
  className,
  style
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showConflicts, setShowConflicts] = useState(true);

  const displayWeekDays = showWeekend ? weekDays : weekDays.slice(0, 5);
  const cellHeight = Math.round(80 * (zoomLevel / 100));

  // 构建课程表网格数据
  const scheduleGrid = useMemo(() => {
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
      const dayIndex = item.day_of_week - 1;
      
      if (grid[timeSlot] && dayIndex >= 0 && dayIndex < displayWeekDays.length) {
        grid[timeSlot][dayIndex] = item;
      }
    });

    return grid;
  }, [scheduleData, timeSlots, displayWeekDays]);

  // 检测冲突
  const conflicts = useMemo(() => {
    const conflictMap: Record<string, ScheduleItem[]> = {};
    
    scheduleData.forEach(item => {
      const key = `${item.day_of_week}-${item.start_time}-${item.end_time}`;
      if (!conflictMap[key]) {
        conflictMap[key] = [];
      }
      conflictMap[key].push(item);
    });

    return Object.values(conflictMap).filter(items => items.length > 1);
  }, [scheduleData]);

  const handleDrop = useCallback((item: any, dayIndex: number, timeSlotIndex: number) => {
    if (onItemMove && item.course) {
      onItemMove(item.course, dayIndex + 1, timeSlotIndex);
    }
  }, [onItemMove]);

  const renderGridView = () => (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ 
        width: '100%', 
        minWidth: showWeekend ? '900px' : '700px', 
        borderCollapse: 'collapse',
        transform: `scale(${zoomLevel / 100})`,
        transformOrigin: 'top left'
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
              {displayWeekDays.map((_, dayIndex) => {
                const course = scheduleGrid[timeSlot]?.[dayIndex];
                
                if (enableDragDrop) {
                  return (
                    <DroppableCell
                      key={dayIndex}
                      dayIndex={dayIndex}
                      timeSlotIndex={timeIndex}
                      cellHeight={cellHeight}
                      onDrop={handleDrop}
                    >
                      {course && (
                        <DraggableCourseCell
                          course={course}
                          dayIndex={dayIndex}
                          timeSlotIndex={timeIndex}
                          cellHeight={cellHeight}
                          onCellClick={onCellClick}
                          enableDrag={mode === 'edit'}
                        />
                      )}
                    </DroppableCell>
                  );
                }

                return (
                  <td
                    key={dayIndex}
                    style={{
                      padding: '4px',
                      border: '1px solid #d9d9d9',
                      verticalAlign: 'top',
                      height: `${cellHeight}px`
                    }}
                  >
                    {course && (
                      <DraggableCourseCell
                        course={course}
                        dayIndex={dayIndex}
                        timeSlotIndex={timeIndex}
                        cellHeight={cellHeight}
                        onCellClick={onCellClick}
                        enableDrag={false}
                      />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderListView = () => (
    <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
      {scheduleData.map((item, index) => (
        <Card
          key={index}
          size="small"
          style={{ marginBottom: '8px' }}
          onClick={() => onCellClick?.(item, item.day_of_week - 1, 0)}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Text strong>{item.course_name}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {weekDays[item.day_of_week - 1]} {item.start_time}-{item.end_time}
              </Text>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '12px', color: '#666' }}>
                <EnvironmentOutlined /> {item.classroom || '待安排'}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                <UserOutlined /> {item.teacher_name || '待分配'}
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  const renderCalendarView = () => (
    <div>
      <Text>日历视图开发中...</Text>
    </div>
  );

  const renderContent = () => {
    switch (viewMode) {
      case 'list':
        return renderListView();
      case 'calendar':
        return renderCalendarView();
      default:
        return renderGridView();
    }
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

  const content = (
    <Card 
      className={className} 
      style={{
        ...style,
        height: isFullscreen ? '100vh' : 'auto',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 1000 : 'auto',
      }}
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>课程表</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {enableMultiView && (
              <Select
                value={viewMode}
                onChange={setViewMode}
                size="small"
                style={{ width: 100 }}
              >
                <Option value="grid"><TableOutlined /> 表格</Option>
                <Option value="list"><AppstoreOutlined /> 列表</Option>
                <Option value="calendar"><CalendarOutlined /> 日历</Option>
              </Select>
            )}
            
            {enableZoom && viewMode === 'grid' && (
              <>
                <Button
                  size="small"
                  icon={<ZoomOutOutlined />}
                  onClick={() => setZoomLevel(Math.max(50, zoomLevel - 25))}
                  disabled={zoomLevel <= 50}
                />
                <Slider
                  min={50}
                  max={200}
                  step={25}
                  value={zoomLevel}
                  onChange={setZoomLevel}
                  style={{ width: 100 }}
                  tooltip={{ formatter: (value) => `${value}%` }}
                />
                <Button
                  size="small"
                  icon={<ZoomInOutlined />}
                  onClick={() => setZoomLevel(Math.min(200, zoomLevel + 25))}
                  disabled={zoomLevel >= 200}
                />
              </>
            )}
            
            <Button
              size="small"
              icon={isFullscreen ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setIsFullscreen(!isFullscreen)}
            />
          </div>
        </div>
      }
      extra={
        conflicts.length > 0 && showConflicts && (
          <Tag color="warning">
            发现 {conflicts.length} 个时间冲突
          </Tag>
        )
      }
    >
      {renderContent()}
      
      {/* 图例和说明 */}
      {viewMode === 'grid' && (
        <div style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: '#fafafa',
          borderRadius: '4px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ fontSize: '12px', color: '#666' }}>
              <BookOutlined style={{ marginRight: '4px' }} />
              {enableDragDrop && mode === 'edit' 
                ? '拖拽课程单元格可调整时间安排' 
                : '点击课程单元格查看详细信息'
              }
            </Text>
            
            {conflicts.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Text style={{ fontSize: '12px', color: '#666' }}>显示冲突:</Text>
                <Switch
                  size="small"
                  checked={showConflicts}
                  onChange={setShowConflicts}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );

  // return enableDragDrop ? (
  //   <DndProvider backend={HTML5Backend}>
  //     {content}
  //   </DndProvider>
  // ) : content;
  return content;
};

export default EnhancedScheduleGrid;

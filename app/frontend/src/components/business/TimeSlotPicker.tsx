import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Tag, message } from 'antd';
import { ClockCircleOutlined, CheckOutlined } from '@ant-design/icons';

interface TimeSlot {
  id: string;
  name: string;
  startTime: string;
  endTime: string;
  duration: number;
  order: number;
}

interface SelectedSlot {
  dayOfWeek: number;
  timeSlotId: string;
  timeSlot: TimeSlot;
}

interface TimeSlotPickerProps {
  value?: SelectedSlot[];
  onChange?: (value: SelectedSlot[]) => void;
  disabled?: boolean;
  multiple?: boolean;
  conflictSlots?: SelectedSlot[];
  maxSelections?: number;
}

const TimeSlotPicker: React.FC<TimeSlotPickerProps> = ({
  value = [],
  onChange,
  disabled = false,
  multiple = true,
  conflictSlots = [],
  maxSelections,
}) => {
  const [selectedSlots, setSelectedSlots] = useState<SelectedSlot[]>(value);

  // 预定义时间段
  const timeSlots: TimeSlot[] = [
    {
      id: '1',
      name: '第1节',
      startTime: '08:00',
      endTime: '10:00',
      duration: 120,
      order: 1,
    },
    {
      id: '2',
      name: '第2节',
      startTime: '10:10',
      endTime: '12:10',
      duration: 120,
      order: 2,
    },
    {
      id: '3',
      name: '第3节',
      startTime: '14:00',
      endTime: '16:00',
      duration: 120,
      order: 3,
    },
    {
      id: '4',
      name: '第4节',
      startTime: '16:10',
      endTime: '18:10',
      duration: 120,
      order: 4,
    },
    {
      id: '5',
      name: '第5节',
      startTime: '19:00',
      endTime: '21:00',
      duration: 120,
      order: 5,
    },
  ];

  const weekDays = [
    { id: 1, name: '周一', shortName: '一' },
    { id: 2, name: '周二', shortName: '二' },
    { id: 3, name: '周三', shortName: '三' },
    { id: 4, name: '周四', shortName: '四' },
    { id: 5, name: '周五', shortName: '五' },
    { id: 6, name: '周六', shortName: '六' },
    { id: 7, name: '周日', shortName: '日' },
  ];

  useEffect(() => {
    setSelectedSlots(value);
  }, [value]);

  const isSlotSelected = (dayOfWeek: number, timeSlotId: string): boolean => {
    return selectedSlots.some(
      slot => slot.dayOfWeek === dayOfWeek && slot.timeSlotId === timeSlotId
    );
  };

  const isSlotConflict = (dayOfWeek: number, timeSlotId: string): boolean => {
    return conflictSlots.some(
      slot => slot.dayOfWeek === dayOfWeek && slot.timeSlotId === timeSlotId
    );
  };

  const handleSlotClick = (dayOfWeek: number, timeSlot: TimeSlot) => {
    if (disabled) return;

    const isSelected = isSlotSelected(dayOfWeek, timeSlot.id);
    const isConflict = isSlotConflict(dayOfWeek, timeSlot.id);

    if (isConflict && !isSelected) {
      message.warning('该时间段存在冲突，无法选择');
      return;
    }

    let newSelectedSlots: SelectedSlot[];

    if (isSelected) {
      // 取消选择
      newSelectedSlots = selectedSlots.filter(
        slot => !(slot.dayOfWeek === dayOfWeek && slot.timeSlotId === timeSlot.id)
      );
    } else {
      // 选择时间段
      if (!multiple) {
        // 单选模式，清空之前的选择
        newSelectedSlots = [{
          dayOfWeek,
          timeSlotId: timeSlot.id,
          timeSlot,
        }];
      } else {
        // 多选模式
        if (maxSelections && selectedSlots.length >= maxSelections) {
          message.warning(`最多只能选择 ${maxSelections} 个时间段`);
          return;
        }

        newSelectedSlots = [
          ...selectedSlots,
          {
            dayOfWeek,
            timeSlotId: timeSlot.id,
            timeSlot,
          },
        ];
      }
    }

    setSelectedSlots(newSelectedSlots);
    onChange?.(newSelectedSlots);
  };

  // const getSlotButtonType = (dayOfWeek: number, timeSlotId: string) => {
  //   if (isSlotSelected(dayOfWeek, timeSlotId)) {
  //     return 'primary';
  //   }
  //   if (isSlotConflict(dayOfWeek, timeSlotId)) {
  //     return 'danger';
  //   }
  //   return 'default';
  // };

  const getSlotButtonStyle = (dayOfWeek: number, timeSlotId: string) => {
    const baseStyle = {
      width: '100%',
      height: '60px',
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: '12px',
      border: '1px solid #d9d9d9',
      borderRadius: '6px',
      cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'all 0.3s ease',
    };

    if (isSlotSelected(dayOfWeek, timeSlotId)) {
      return {
        ...baseStyle,
        backgroundColor: '#1890ff',
        borderColor: '#1890ff',
        color: '#fff',
      };
    }

    if (isSlotConflict(dayOfWeek, timeSlotId)) {
      return {
        ...baseStyle,
        backgroundColor: '#fff2f0',
        borderColor: '#ffccc7',
        color: '#ff4d4f',
        cursor: 'not-allowed',
      };
    }

    return {
      ...baseStyle,
      backgroundColor: '#fff',
      borderColor: '#d9d9d9',
      color: '#666',
    };
  };

  const clearSelection = () => {
    setSelectedSlots([]);
    onChange?.([]);
  };

  return (
    <div className="time-slot-picker">
      <Card
        title={
          <Space>
            <ClockCircleOutlined />
            <span>选择上课时间</span>
            {selectedSlots.length > 0 && (
              <Tag color="blue">{selectedSlots.length} 个时间段</Tag>
            )}
          </Space>
        }
        extra={
          selectedSlots.length > 0 && (
            <Button size="small" onClick={clearSelection}>
              清空选择
            </Button>
          )
        }
        size="small"
      >
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'separate', borderSpacing: '4px' }}>
            <thead>
              <tr>
                <th style={{ 
                  width: '80px', 
                  textAlign: 'center',
                  padding: '8px',
                  backgroundColor: '#fafafa',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 'bold'
                }}>
                  时间
                </th>
                {weekDays.map(day => (
                  <th key={day.id} style={{ 
                    textAlign: 'center',
                    padding: '8px',
                    backgroundColor: '#fafafa',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: 'bold'
                  }}>
                    {day.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {timeSlots.map(timeSlot => (
                <tr key={timeSlot.id}>
                  <td style={{ 
                    textAlign: 'center',
                    padding: '4px',
                    backgroundColor: '#fafafa',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    verticalAlign: 'middle'
                  }}>
                    <div>{timeSlot.name}</div>
                    <div style={{ fontSize: '10px', color: '#999', marginTop: '2px' }}>
                      {timeSlot.startTime}-{timeSlot.endTime}
                    </div>
                  </td>
                  {weekDays.map(day => (
                    <td key={`${day.id}-${timeSlot.id}`} style={{ padding: '4px' }}>
                      <div
                        style={getSlotButtonStyle(day.id, timeSlot.id)}
                        onClick={() => handleSlotClick(day.id, timeSlot)}
                      >
                        <div style={{ fontWeight: 'bold' }}>
                          {timeSlot.name}
                        </div>
                        <div style={{ fontSize: '10px', opacity: 0.8 }}>
                          {timeSlot.startTime}-{timeSlot.endTime}
                        </div>
                        {isSlotSelected(day.id, timeSlot.id) && (
                          <CheckOutlined style={{ 
                            position: 'absolute',
                            top: '4px',
                            right: '4px',
                            fontSize: '12px'
                          }} />
                        )}
                        {isSlotConflict(day.id, timeSlot.id) && (
                          <div style={{ fontSize: '10px', marginTop: '2px' }}>
                            冲突
                          </div>
                        )}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 选择结果显示 */}
        {selectedSlots.length > 0 && (
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f6ffed', borderRadius: '6px' }}>
            <div style={{ marginBottom: '8px', fontSize: '13px', fontWeight: 'bold', color: '#52c41a' }}>
              已选择的时间段：
            </div>
            <Space wrap>
              {selectedSlots.map((slot, index) => (
                <Tag
                  key={`${slot.dayOfWeek}-${slot.timeSlotId}`}
                  color="green"
                  closable={!disabled}
                  onClose={() => {
                    const newSlots = selectedSlots.filter((_, i) => i !== index);
                    setSelectedSlots(newSlots);
                    onChange?.(newSlots);
                  }}
                >
                  {weekDays.find(d => d.id === slot.dayOfWeek)?.name} {slot.timeSlot.name}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {/* 说明文字 */}
        <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
          <Space direction="vertical" size="small">
            <div>• 点击时间格子进行选择，再次点击可取消选择</div>
            <div>• 红色表示时间冲突，无法选择</div>
            <div>• 蓝色表示已选择的时间段</div>
            {maxSelections && (
              <div>• 最多可选择 {maxSelections} 个时间段</div>
            )}
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default TimeSlotPicker;

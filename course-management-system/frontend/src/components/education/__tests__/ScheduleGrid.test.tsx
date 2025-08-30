import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScheduleGrid from '../ScheduleGrid';

// Mock schedule data
const mockScheduleData = [
  {
    id: 1,
    courseId: 1,
    courseName: '高等数学',
    courseCode: 'MATH101',
    teacher: '张教授',
    classroom: 'A101',
    timeSlot: '第1-2节',
    dayOfWeek: 1, // Monday
    startTime: '08:00',
    endTime: '09:40',
    weeks: '1-16周',
    color: '#1890ff',
  },
  {
    id: 2,
    courseId: 2,
    courseName: '线性代数',
    courseCode: 'MATH102',
    teacher: '李教授',
    classroom: 'A102',
    timeSlot: '第3-4节',
    dayOfWeek: 1, // Monday
    startTime: '10:00',
    endTime: '11:40',
    weeks: '1-16周',
    color: '#52c41a',
  },
  {
    id: 3,
    courseId: 3,
    courseName: '大学物理',
    courseCode: 'PHYS101',
    teacher: '王教授',
    classroom: 'B201',
    timeSlot: '第1-2节',
    dayOfWeek: 2, // Tuesday
    startTime: '08:00',
    endTime: '09:40',
    weeks: '1-16周',
    color: '#fa8c16',
  },
];

const mockTimeSlots = [
  { id: 1, name: '第1-2节', startTime: '08:00', endTime: '09:40' },
  { id: 2, name: '第3-4节', startTime: '10:00', endTime: '11:40' },
  { id: 3, name: '第5-6节', startTime: '14:00', endTime: '15:40' },
  { id: 4, name: '第7-8节', startTime: '16:00', endTime: '17:40' },
  { id: 5, name: '第9-10节', startTime: '19:00', endTime: '20:40' },
];

describe('ScheduleGrid', () => {
  it('renders schedule grid with correct structure', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    // Check if weekday headers are rendered
    expect(screen.getByText('周一')).toBeInTheDocument();
    expect(screen.getByText('周二')).toBeInTheDocument();
    expect(screen.getByText('周三')).toBeInTheDocument();
    expect(screen.getByText('周四')).toBeInTheDocument();
    expect(screen.getByText('周五')).toBeInTheDocument();

    // Check if time slots are rendered
    expect(screen.getByText('第1-2节')).toBeInTheDocument();
    expect(screen.getByText('第3-4节')).toBeInTheDocument();
    expect(screen.getByText('08:00-09:40')).toBeInTheDocument();
    expect(screen.getByText('10:00-11:40')).toBeInTheDocument();
  });

  it('displays course information in schedule cells', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    // Check if course names are displayed
    expect(screen.getByText('高等数学')).toBeInTheDocument();
    expect(screen.getByText('线性代数')).toBeInTheDocument();
    expect(screen.getByText('大学物理')).toBeInTheDocument();

    // Check if teacher names are displayed
    expect(screen.getByText('张教授')).toBeInTheDocument();
    expect(screen.getByText('李教授')).toBeInTheDocument();
    expect(screen.getByText('王教授')).toBeInTheDocument();

    // Check if classroom information is displayed
    expect(screen.getByText('A101')).toBeInTheDocument();
    expect(screen.getByText('A102')).toBeInTheDocument();
    expect(screen.getByText('B201')).toBeInTheDocument();
  });

  it('handles empty schedule data', () => {
    render(
      <ScheduleGrid 
        schedules={[]} 
        timeSlots={mockTimeSlots}
      />
    );

    // Should still render the grid structure
    expect(screen.getByText('周一')).toBeInTheDocument();
    expect(screen.getByText('第1-2节')).toBeInTheDocument();
    
    // But no course information should be displayed
    expect(screen.queryByText('高等数学')).not.toBeInTheDocument();
  });

  it('calls onCellClick when a schedule cell is clicked', () => {
    const mockOnCellClick = jest.fn();
    
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        onCellClick={mockOnCellClick}
      />
    );

    const courseCell = screen.getByText('高等数学').closest('.schedule-cell');
    fireEvent.click(courseCell!);
    
    expect(mockOnCellClick).toHaveBeenCalledWith(
      expect.objectContaining({
        courseId: 1,
        courseName: '高等数学',
      })
    );
  });

  it('calls onEmptyCellClick when an empty cell is clicked', () => {
    const mockOnEmptyCellClick = jest.fn();
    
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        onEmptyCellClick={mockOnEmptyCellClick}
      />
    );

    // Find an empty cell (e.g., Wednesday first period)
    const emptyCells = screen.getAllByTestId('empty-schedule-cell');
    fireEvent.click(emptyCells[0]);
    
    expect(mockOnEmptyCellClick).toHaveBeenCalledWith(
      expect.objectContaining({
        dayOfWeek: expect.any(Number),
        timeSlotId: expect.any(Number),
      })
    );
  });

  it('shows weekend columns when showWeekend is true', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        showWeekend={true}
      />
    );

    expect(screen.getByText('周六')).toBeInTheDocument();
    expect(screen.getByText('周日')).toBeInTheDocument();
  });

  it('hides weekend columns when showWeekend is false', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        showWeekend={false}
      />
    );

    expect(screen.queryByText('周六')).not.toBeInTheDocument();
    expect(screen.queryByText('周日')).not.toBeInTheDocument();
  });

  it('applies custom colors to schedule items', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    const mathCourseCell = screen.getByText('高等数学').closest('.schedule-item');
    expect(mathCourseCell).toHaveStyle('background-color: #1890ff');
  });

  it('handles schedule conflicts by stacking items', () => {
    const conflictingSchedules = [
      ...mockScheduleData,
      {
        id: 4,
        courseId: 4,
        courseName: '冲突课程',
        courseCode: 'CONF101',
        teacher: '赵教授',
        classroom: 'A103',
        timeSlot: '第1-2节',
        dayOfWeek: 1, // Same as first course
        startTime: '08:00',
        endTime: '09:40',
        weeks: '1-16周',
        color: '#f5222d',
      },
    ];

    render(
      <ScheduleGrid 
        schedules={conflictingSchedules} 
        timeSlots={mockTimeSlots}
      />
    );

    // Both courses should be visible
    expect(screen.getByText('高等数学')).toBeInTheDocument();
    expect(screen.getByText('冲突课程')).toBeInTheDocument();
    
    // Check if conflict indicator is shown
    expect(screen.getByTestId('schedule-conflict')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        loading={true}
      />
    );

    expect(screen.getByTestId('schedule-grid-loading')).toBeInTheDocument();
  });

  it('displays current time indicator', () => {
    // Mock current time to be during class hours
    const mockDate = new Date('2024-01-15T08:30:00'); // Monday 8:30 AM
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
        showCurrentTime={true}
      />
    );

    expect(screen.getByTestId('current-time-indicator')).toBeInTheDocument();

    // Restore Date
    (global.Date as any).mockRestore();
  });

  it('handles responsive layout', () => {
    // Mock window.innerWidth for mobile view
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });

    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    const grid = screen.getByTestId('schedule-grid');
    expect(grid).toHaveClass('schedule-grid-mobile');
  });

  it('supports keyboard navigation', () => {
    render(
      <ScheduleGrid 
        schedules={mockScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    const firstCell = screen.getByText('高等数学').closest('.schedule-cell');
    
    // Focus the cell
    firstCell?.focus();
    expect(firstCell).toHaveFocus();
    
    // Test arrow key navigation
    fireEvent.keyDown(firstCell!, { key: 'ArrowRight' });
    // Should move focus to next cell
  });
});

// Performance tests
describe('ScheduleGrid Performance', () => {
  it('renders large schedule data efficiently', () => {
    const largeScheduleData = Array.from({ length: 100 }, (_, index) => ({
      id: index + 1,
      courseId: index + 1,
      courseName: `课程${index + 1}`,
      courseCode: `COURSE${index + 1}`,
      teacher: `教师${index + 1}`,
      classroom: `教室${index + 1}`,
      timeSlot: '第1-2节',
      dayOfWeek: (index % 5) + 1,
      startTime: '08:00',
      endTime: '09:40',
      weeks: '1-16周',
      color: '#1890ff',
    }));

    const startTime = performance.now();
    
    render(
      <ScheduleGrid 
        schedules={largeScheduleData} 
        timeSlots={mockTimeSlots}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within reasonable time (adjust threshold as needed)
    expect(renderTime).toBeLessThan(1000); // 1 second
  });
});

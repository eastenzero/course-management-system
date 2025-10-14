import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import GradeTable from '../GradeTable';

// Mock grade data
const mockGrades = [
  {
    id: 1,
    studentId: 'S001',
    studentName: '张三',
    courseId: 1,
    courseName: '高等数学',
    courseCode: 'MATH101',
    assignments: [
      { name: '作业1', score: 85, maxScore: 100, weight: 0.1 },
      { name: '作业2', score: 90, maxScore: 100, weight: 0.1 },
    ],
    midtermExam: { score: 88, maxScore: 100, weight: 0.3 },
    finalExam: { score: 92, maxScore: 100, weight: 0.5 },
    totalScore: 89.5,
    letterGrade: 'A',
    gpa: 4.0,
    semester: '2024-2025-1',
  },
  {
    id: 2,
    studentId: 'S002',
    studentName: '李四',
    courseId: 1,
    courseName: '高等数学',
    courseCode: 'MATH101',
    assignments: [
      { name: '作业1', score: 75, maxScore: 100, weight: 0.1 },
      { name: '作业2', score: 80, maxScore: 100, weight: 0.1 },
    ],
    midtermExam: { score: 78, maxScore: 100, weight: 0.3 },
    finalExam: { score: 82, maxScore: 100, weight: 0.5 },
    totalScore: 79.5,
    letterGrade: 'B',
    gpa: 3.0,
    semester: '2024-2025-1',
  },
];

const mockColumns = [
  { key: 'studentName', title: '学生姓名', width: 120 },
  { key: 'studentId', title: '学号', width: 100 },
  { key: 'assignments', title: '平时成绩', width: 120 },
  { key: 'midtermExam', title: '期中考试', width: 100 },
  { key: 'finalExam', title: '期末考试', width: 100 },
  { key: 'totalScore', title: '总成绩', width: 100 },
  { key: 'letterGrade', title: '等级', width: 80 },
];

describe('GradeTable', () => {
  it('renders grade table with correct data', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
      />
    );

    // Check if student names are displayed
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('李四')).toBeInTheDocument();

    // Check if student IDs are displayed
    expect(screen.getByText('S001')).toBeInTheDocument();
    expect(screen.getByText('S002')).toBeInTheDocument();

    // Check if grades are displayed
    expect(screen.getByText('89.5')).toBeInTheDocument();
    expect(screen.getByText('79.5')).toBeInTheDocument();

    // Check if letter grades are displayed
    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });

  it('displays column headers correctly', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
      />
    );

    // Check if all column headers are present
    expect(screen.getByText('学生姓名')).toBeInTheDocument();
    expect(screen.getByText('学号')).toBeInTheDocument();
    expect(screen.getByText('平时成绩')).toBeInTheDocument();
    expect(screen.getByText('期中考试')).toBeInTheDocument();
    expect(screen.getByText('期末考试')).toBeInTheDocument();
    expect(screen.getByText('总成绩')).toBeInTheDocument();
    expect(screen.getByText('等级')).toBeInTheDocument();
  });

  it('handles empty grade data', () => {
    render(
      <GradeTable 
        grades={[]}
        columns={mockColumns}
      />
    );

    // Should show empty state
    expect(screen.getByText('暂无成绩数据')).toBeInTheDocument();
  });

  it('supports sorting by different columns', async () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        sortable
      />
    );

    // Click on total score column to sort
    const totalScoreHeader = screen.getByText('总成绩');
    fireEvent.click(totalScoreHeader);

    await waitFor(() => {
      const rows = screen.getAllByRole('row');
      // First data row should now be 张三 (higher score)
      expect(rows[1]).toHaveTextContent('张三');
    });

    // Click again to reverse sort
    fireEvent.click(totalScoreHeader);

    await waitFor(() => {
      const rows = screen.getAllByRole('row');
      // First data row should now be 李四 (lower score)
      expect(rows[1]).toHaveTextContent('李四');
    });
  });

  it('allows editing grades when editable is true', async () => {
    const mockOnGradeChange = jest.fn();
    
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        editable
        onGradeChange={mockOnGradeChange}
      />
    );

    // Find and click on a grade cell to edit
    const gradeCell = screen.getByDisplayValue('89.5');
    fireEvent.click(gradeCell);

    // Change the value
    fireEvent.change(gradeCell, { target: { value: '95' } });
    fireEvent.blur(gradeCell);

    await waitFor(() => {
      expect(mockOnGradeChange).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 1,
          totalScore: 95,
        })
      );
    });
  });

  it('validates grade input values', async () => {
    const mockOnGradeChange = jest.fn();
    
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        editable
        onGradeChange={mockOnGradeChange}
      />
    );

    const gradeCell = screen.getByDisplayValue('89.5');
    fireEvent.click(gradeCell);

    // Try to enter invalid value
    fireEvent.change(gradeCell, { target: { value: '150' } });
    fireEvent.blur(gradeCell);

    // Should show validation error
    expect(screen.getByText('成绩不能超过100分')).toBeInTheDocument();
    expect(mockOnGradeChange).not.toHaveBeenCalled();
  });

  it('calculates and displays statistics', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        showStatistics
      />
    );

    // Check if statistics are displayed
    expect(screen.getByText('平均分: 84.5')).toBeInTheDocument();
    expect(screen.getByText('最高分: 89.5')).toBeInTheDocument();
    expect(screen.getByText('最低分: 79.5')).toBeInTheDocument();
    expect(screen.getByText('及格率: 100%')).toBeInTheDocument();
  });

  it('supports filtering by student name', async () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        filterable
      />
    );

    const searchInput = screen.getByPlaceholderText('搜索学生姓名');
    fireEvent.change(searchInput, { target: { value: '张三' } });

    await waitFor(() => {
      expect(screen.getByText('张三')).toBeInTheDocument();
      expect(screen.queryByText('李四')).not.toBeInTheDocument();
    });
  });

  it('exports grade data when export button is clicked', () => {
    const mockOnExport = jest.fn();
    
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        exportable
        onExport={mockOnExport}
      />
    );

    const exportButton = screen.getByText('导出');
    fireEvent.click(exportButton);

    expect(mockOnExport).toHaveBeenCalledWith(mockGrades);
  });

  it('handles row selection', () => {
    const mockOnSelectionChange = jest.fn();
    
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        selectable
        onSelectionChange={mockOnSelectionChange}
      />
    );

    // Select first row
    const firstCheckbox = screen.getAllByRole('checkbox')[1]; // Skip header checkbox
    fireEvent.click(firstCheckbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith([mockGrades[0]]);
  });

  it('supports bulk operations on selected rows', () => {
    const mockOnBulkOperation = jest.fn();
    
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        selectable
        onBulkOperation={mockOnBulkOperation}
      />
    );

    // Select multiple rows
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // First data row
    fireEvent.click(checkboxes[2]); // Second data row

    // Perform bulk operation
    const bulkActionButton = screen.getByText('批量操作');
    fireEvent.click(bulkActionButton);

    const deleteOption = screen.getByText('删除选中');
    fireEvent.click(deleteOption);

    expect(mockOnBulkOperation).toHaveBeenCalledWith('delete', [mockGrades[0], mockGrades[1]]);
  });

  it('shows loading state', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        loading
      />
    );

    expect(screen.getByTestId('grade-table-loading')).toBeInTheDocument();
  });

  it('handles pagination for large datasets', () => {
    const largeGradeData = Array.from({ length: 50 }, (_, index) => ({
      ...mockGrades[0],
      id: index + 1,
      studentId: `S${(index + 1).toString().padStart(3, '0')}`,
      studentName: `学生${index + 1}`,
    }));

    render(
      <GradeTable 
        grades={largeGradeData}
        columns={mockColumns}
        pagination={{ pageSize: 10 }}
      />
    );

    // Should show pagination controls
    expect(screen.getByText('1')).toBeInTheDocument(); // Page 1
    expect(screen.getByText('下一页')).toBeInTheDocument();
    
    // Should only show first 10 students
    expect(screen.getByText('学生1')).toBeInTheDocument();
    expect(screen.getByText('学生10')).toBeInTheDocument();
    expect(screen.queryByText('学生11')).not.toBeInTheDocument();
  });

  it('displays grade distribution chart when enabled', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        showChart
      />
    );

    expect(screen.getByTestId('grade-distribution-chart')).toBeInTheDocument();
  });

  it('handles responsive layout on mobile devices', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });

    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
      />
    );

    const table = screen.getByRole('table');
    expect(table).toHaveClass('grade-table-mobile');
  });
});

// Accessibility tests
describe('GradeTable Accessibility', () => {
  it('has proper ARIA labels and roles', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
      />
    );

    const table = screen.getByRole('table');
    expect(table).toHaveAttribute('aria-label', '成绩表');

    const columnHeaders = screen.getAllByRole('columnheader');
    expect(columnHeaders).toHaveLength(mockColumns.length);

    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(mockGrades.length + 1); // +1 for header
  });

  it('supports keyboard navigation', () => {
    render(
      <GradeTable 
        grades={mockGrades}
        columns={mockColumns}
        editable
      />
    );

    const firstCell = screen.getByDisplayValue('89.5');
    firstCell.focus();
    
    // Test Tab navigation
    fireEvent.keyDown(firstCell, { key: 'Tab' });
    // Should move to next editable cell
    
    // Test Enter to edit
    fireEvent.keyDown(firstCell, { key: 'Enter' });
    expect(firstCell).toHaveAttribute('contentEditable', 'true');
  });
});

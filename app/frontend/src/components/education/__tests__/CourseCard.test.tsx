import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import CourseCard from '../CourseCard';

// Mock course data
const mockCourse = {
  id: 1,
  name: '高等数学',
  code: 'MATH101',
  credits: 4,
  hours: 64,
  department: '数学系',
  teacher: '张教授',
  semester: '2024-2025-1',
  description: '高等数学基础课程',
  enrollmentCount: 45,
  maxStudents: 50,
  status: 'active' as const,
};

// Wrapper component for router context
const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('CourseCard', () => {
  it('renders course information correctly', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );

    // Check if course name and code are displayed
    expect(screen.getByText('高等数学')).toBeInTheDocument();
    expect(screen.getByText('MATH101')).toBeInTheDocument();
    
    // Check if teacher name is displayed
    expect(screen.getByText('张教授')).toBeInTheDocument();
    
    // Check if department is displayed
    expect(screen.getByText('数学系')).toBeInTheDocument();
    
    // Check if credits and hours are displayed
    expect(screen.getByText('4学分')).toBeInTheDocument();
    expect(screen.getByText('64学时')).toBeInTheDocument();
  });

  it('displays enrollment information', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );

    // Check enrollment count
    expect(screen.getByText('45/50')).toBeInTheDocument();
  });

  it('shows course status correctly', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );

    // Check if status is displayed (assuming there's a status indicator)
    const statusElement = screen.getByText('进行中');
    expect(statusElement).toBeInTheDocument();
  });

  it('handles course with different status', () => {
    const inactiveCourse = { ...mockCourse, status: 'inactive' as const };
    
    render(
      <RouterWrapper>
        <CourseCard course={inactiveCourse} />
      </RouterWrapper>
    );

    expect(screen.getByText('已结束')).toBeInTheDocument();
  });

  it('handles course at full capacity', () => {
    const fullCourse = { ...mockCourse, enrollmentCount: 50 };
    
    render(
      <RouterWrapper>
        <CourseCard course={fullCourse} />
      </RouterWrapper>
    );

    expect(screen.getByText('50/50')).toBeInTheDocument();
    // Check if full capacity indicator is shown
    expect(screen.getByText('已满')).toBeInTheDocument();
  });

  it('calls onClick handler when card is clicked', () => {
    const mockOnClick = jest.fn();
    
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} onClick={mockOnClick} />
      </RouterWrapper>
    );

    const card = screen.getByRole('article');
    fireEvent.click(card);
    
    expect(mockOnClick).toHaveBeenCalledWith(mockCourse);
  });

  it('navigates to course detail when clicked without onClick handler', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );

    const card = screen.getByRole('article');
    expect(card).toBeInTheDocument();
    
    // Check if the card has the correct link or navigation behavior
    fireEvent.click(card);
    // Note: In a real test, you might want to mock useNavigate and check if it was called
  });

  it('displays course description when provided', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} showDescription />
      </RouterWrapper>
    );

    expect(screen.getByText('高等数学基础课程')).toBeInTheDocument();
  });

  it('hides course description when showDescription is false', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} showDescription={false} />
      </RouterWrapper>
    );

    expect(screen.queryByText('高等数学基础课程')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-course-card';
    
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} className={customClass} />
      </RouterWrapper>
    );

    const card = screen.getByRole('article');
    expect(card).toHaveClass(customClass);
  });

  it('handles course without teacher', () => {
    const courseWithoutTeacher = { ...mockCourse, teacher: undefined };
    
    render(
      <RouterWrapper>
        <CourseCard course={courseWithoutTeacher} />
      </RouterWrapper>
    );

    expect(screen.getByText('待分配')).toBeInTheDocument();
  });

  it('handles course with long name', () => {
    const longNameCourse = {
      ...mockCourse,
      name: '这是一个非常非常长的课程名称用来测试文本截断功能'
    };
    
    render(
      <RouterWrapper>
        <CourseCard course={longNameCourse} />
      </RouterWrapper>
    );

    const nameElement = screen.getByText(longNameCourse.name);
    expect(nameElement).toBeInTheDocument();
  });

  it('shows loading state when course data is loading', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} loading />
      </RouterWrapper>
    );

    // Check if loading skeleton or indicator is shown
    expect(screen.getByTestId('course-card-loading')).toBeInTheDocument();
  });

  it('handles hover effects', () => {
    render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );

    const card = screen.getByRole('article');
    
    fireEvent.mouseEnter(card);
    expect(card).toHaveClass('course-card-hover');
    
    fireEvent.mouseLeave(card);
    expect(card).not.toHaveClass('course-card-hover');
  });
});

// Snapshot tests
describe('CourseCard Snapshots', () => {
  it('matches snapshot for default course card', () => {
    const { container } = render(
      <RouterWrapper>
        <CourseCard course={mockCourse} />
      </RouterWrapper>
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for course card with description', () => {
    const { container } = render(
      <RouterWrapper>
        <CourseCard course={mockCourse} showDescription />
      </RouterWrapper>
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for full capacity course', () => {
    const fullCourse = { ...mockCourse, enrollmentCount: 50 };
    
    const { container } = render(
      <RouterWrapper>
        <CourseCard course={fullCourse} />
      </RouterWrapper>
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });
});

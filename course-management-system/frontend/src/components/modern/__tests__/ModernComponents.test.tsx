import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// 导入要测试的组件
import WelcomeHeader from '../WelcomeHeader';
import StatisticCard from '../StatisticCard';
import QuickActionButton from '../QuickActionButton';
import ModernButton from '../ModernButton';
import ModernCard from '../ModernCard';

// Mock store
const mockStore = configureStore({
  reducer: {
    auth: (state = { user: { username: 'test', email: 'test@example.com' } }) => state,
  },
});

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Provider store={mockStore}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </Provider>
);

describe('Modern Components', () => {
  describe('WelcomeHeader', () => {
    it('renders teacher welcome header correctly', () => {
      render(
        <TestWrapper>
          <WelcomeHeader
            userType="teacher"
            userName="张老师"
            userInfo={{
              id: 'T001',
              email: 'teacher@example.com',
              title: '教授'
            }}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/张老师/)).toBeInTheDocument();
      expect(screen.getByText(/工号：T001/)).toBeInTheDocument();
      expect(screen.getByText(/职称：教授/)).toBeInTheDocument();
    });

    it('renders student welcome header correctly', () => {
      render(
        <TestWrapper>
          <WelcomeHeader
            userType="student"
            userName="李同学"
            userInfo={{
              id: 'S001',
              email: 'student@example.com',
              major: '计算机科学',
              className: '计科1班'
            }}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/李同学/)).toBeInTheDocument();
      expect(screen.getByText(/学号：S001/)).toBeInTheDocument();
      expect(screen.getByText(/专业：计算机科学/)).toBeInTheDocument();
      expect(screen.getByText(/班级：计科1班/)).toBeInTheDocument();
    });
  });

  describe('StatisticCard', () => {
    it('renders statistic card with correct data', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <StatisticCard
            title="总课程数"
            value={10}
            icon={<span>📚</span>}
            variant="courses"
            onClick={mockClick}
          />
        </TestWrapper>
      );

      expect(screen.getByText('总课程数')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });

    it('handles click events', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <StatisticCard
            title="总课程数"
            value={10}
            icon={<span>📚</span>}
            variant="courses"
            onClick={mockClick}
          />
        </TestWrapper>
      );

      const card = screen.getByText('总课程数').closest('.ant-card');
      if (card) {
        fireEvent.click(card);
        expect(mockClick).toHaveBeenCalledTimes(1);
      }
    });
  });

  describe('QuickActionButton', () => {
    it('renders quick action button correctly', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <QuickActionButton
            icon={<span>📚</span>}
            title="我的课程"
            description="管理您的课程"
            onClick={mockClick}
          />
        </TestWrapper>
      );

      expect(screen.getByText('我的课程')).toBeInTheDocument();
      expect(screen.getByText('管理您的课程')).toBeInTheDocument();
    });

    it('handles click events', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <QuickActionButton
            icon={<span>📚</span>}
            title="我的课程"
            description="管理您的课程"
            onClick={mockClick}
          />
        </TestWrapper>
      );

      const button = screen.getByText('我的课程').closest('button');
      if (button) {
        fireEvent.click(button);
        expect(mockClick).toHaveBeenCalledTimes(1);
      }
    });

    it('disables button when disabled prop is true', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <QuickActionButton
            icon={<span>📚</span>}
            title="我的课程"
            description="管理您的课程"
            onClick={mockClick}
            disabled={true}
          />
        </TestWrapper>
      );

      const button = screen.getByText('我的课程').closest('button');
      expect(button).toBeDisabled();
    });
  });

  describe('ModernButton', () => {
    it('renders modern button correctly', () => {
      render(
        <TestWrapper>
          <ModernButton>测试按钮</ModernButton>
        </TestWrapper>
      );

      expect(screen.getByText('测试按钮')).toBeInTheDocument();
    });

    it('applies correct variant classes', () => {
      render(
        <TestWrapper>
          <ModernButton variant="student">学生按钮</ModernButton>
        </TestWrapper>
      );

      const button = screen.getByText('学生按钮');
      expect(button).toHaveClass('modern-button');
    });
  });

  describe('ModernCard', () => {
    it('renders modern card correctly', () => {
      render(
        <TestWrapper>
          <ModernCard title="测试卡片">
            <p>卡片内容</p>
          </ModernCard>
        </TestWrapper>
      );

      expect(screen.getByText('测试卡片')).toBeInTheDocument();
      expect(screen.getByText('卡片内容')).toBeInTheDocument();
    });

    it('applies correct variant styles', () => {
      render(
        <TestWrapper>
          <ModernCard variant="glass" title="玻璃卡片">
            <p>内容</p>
          </ModernCard>
        </TestWrapper>
      );

      const card = screen.getByText('玻璃卡片').closest('.ant-card');
      expect(card).toHaveClass('modern-card');
    });
  });
});

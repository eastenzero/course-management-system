import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PlusOutlined } from '@ant-design/icons';
import EmptyState from '../EmptyState';

describe('EmptyState', () => {
  it('renders with default props', () => {
    render(<EmptyState />);
    
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
    expect(screen.getByText('当前没有任何数据')).toBeInTheDocument();
  });

  it('renders with custom title and description', () => {
    render(
      <EmptyState
        title="自定义标题"
        description="自定义描述"
      />
    );
    
    expect(screen.getByText('自定义标题')).toBeInTheDocument();
    expect(screen.getByText('自定义描述')).toBeInTheDocument();
  });

  it('renders different types correctly', () => {
    const { rerender } = render(<EmptyState type="search" />);
    expect(screen.getByText('没有找到相关内容')).toBeInTheDocument();

    rerender(<EmptyState type="error" />);
    expect(screen.getByText('加载失败')).toBeInTheDocument();

    rerender(<EmptyState type="loading" />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders primary action button', () => {
    const mockOnClick = jest.fn();
    
    render(
      <EmptyState
        primaryAction={{
          text: '添加数据',
          onClick: mockOnClick,
          icon: <PlusOutlined />,
        }}
      />
    );
    
    const button = screen.getByText('添加数据');
    expect(button).toBeInTheDocument();
    
    fireEvent.click(button);
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders secondary action button', () => {
    const mockOnClick = jest.fn();
    
    render(
      <EmptyState
        secondaryAction={{
          text: '重置',
          onClick: mockOnClick,
        }}
      />
    );
    
    const button = screen.getByText('重置');
    expect(button).toBeInTheDocument();
    
    fireEvent.click(button);
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders both primary and secondary actions', () => {
    const mockPrimaryClick = jest.fn();
    const mockSecondaryClick = jest.fn();
    
    render(
      <EmptyState
        primaryAction={{
          text: '主要操作',
          onClick: mockPrimaryClick,
        }}
        secondaryAction={{
          text: '次要操作',
          onClick: mockSecondaryClick,
        }}
      />
    );
    
    expect(screen.getByText('主要操作')).toBeInTheDocument();
    expect(screen.getByText('次要操作')).toBeInTheDocument();
  });

  it('applies custom styles and className', () => {
    const customStyle = { backgroundColor: 'red' };
    const customClassName = 'custom-empty-state';
    
    render(
      <EmptyState
        style={customStyle}
        className={customClassName}
      />
    );
    
    const container = screen.getByText('暂无数据').closest('div');
    expect(container).toHaveClass(customClassName);
    expect(container).toHaveStyle('background-color: red');
  });

  it('shows/hides image based on showImage prop', () => {
    const { rerender } = render(<EmptyState showImage={false} />);
    
    // 当 showImage 为 false 时，应该显示图标而不是图片
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
    
    rerender(<EmptyState showImage={true} />);
    // 当 showImage 为 true 时，应该显示默认图片
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
  });

  it('renders custom icon when showImage is false', () => {
    const customIcon = <div data-testid="custom-icon">Custom Icon</div>;
    
    render(
      <EmptyState
        icon={customIcon}
        showImage={false}
      />
    );
    
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('handles button types correctly', () => {
    render(
      <EmptyState
        primaryAction={{
          text: '主要按钮',
          onClick: jest.fn(),
          type: 'primary',
        }}
      />
    );
    
    const button = screen.getByText('主要按钮');
    expect(button).toHaveClass('ant-btn-primary');
  });
});

// 快照测试
describe('EmptyState Snapshots', () => {
  it('matches snapshot for default state', () => {
    const { container } = render(<EmptyState />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for search state', () => {
    const { container } = render(<EmptyState type="search" />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for error state', () => {
    const { container } = render(<EmptyState type="error" />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot with actions', () => {
    const { container } = render(
      <EmptyState
        primaryAction={{
          text: '添加',
          onClick: jest.fn(),
        }}
        secondaryAction={{
          text: '重置',
          onClick: jest.fn(),
        }}
      />
    );
    expect(container.firstChild).toMatchSnapshot();
  });
});

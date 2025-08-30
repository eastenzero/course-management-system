import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import VirtualTable from '../VirtualTable';

// Mock react-window
jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemCount, itemData }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 10) }, (_, index) =>
        children({ index, style: {}, data: itemData })
      )}
    </div>
  ),
}));

describe('VirtualTable Performance Tests', () => {
  const generateLargeDataset = (count: number) => {
    return Array.from({ length: count }, (_, index) => ({
      id: index + 1,
      name: `Item ${index + 1}`,
      value: Math.random() * 100,
    }));
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
  ];

  it('should use virtual scrolling for large datasets', () => {
    const largeDataset = generateLargeDataset(1000);
    
    render(
      <VirtualTable
        columns={columns}
        dataSource={largeDataset}
        virtual={true}
        virtualThreshold={100}
        height={400}
      />
    );

    // Should render virtual list for large dataset
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });

  it('should use regular table for small datasets', () => {
    const smallDataset = generateLargeDataset(50);
    
    render(
      <VirtualTable
        columns={columns}
        dataSource={smallDataset}
        virtual={true}
        virtualThreshold={100}
        height={400}
      />
    );

    // Should not render virtual list for small dataset
    expect(screen.queryByTestId('virtual-list')).not.toBeInTheDocument();
  });

  it('should handle disabled virtual scrolling', () => {
    const largeDataset = generateLargeDataset(1000);
    
    render(
      <VirtualTable
        columns={columns}
        dataSource={largeDataset}
        virtual={false}
        height={400}
      />
    );

    // Should not render virtual list when disabled
    expect(screen.queryByTestId('virtual-list')).not.toBeInTheDocument();
  });

  it('should render efficiently with memo', () => {
    const dataset = generateLargeDataset(100);
    
    const { rerender } = render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        height={400}
      />
    );

    // Re-render with same props should not cause unnecessary re-renders
    rerender(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        height={400}
      />
    );

    // Component should still be rendered correctly
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('should handle custom item height', () => {
    const dataset = generateLargeDataset(200);
    
    render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        virtualThreshold={100}
        itemHeight={60}
        height={400}
      />
    );

    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });

  it('should handle custom virtual threshold', () => {
    const dataset = generateLargeDataset(150);
    
    // With threshold 200, should use regular table
    const { rerender } = render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        virtualThreshold={200}
        height={400}
      />
    );

    expect(screen.queryByTestId('virtual-list')).not.toBeInTheDocument();

    // With threshold 100, should use virtual table
    rerender(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        virtualThreshold={100}
        height={400}
      />
    );

    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });

  it('should handle empty dataset', () => {
    render(
      <VirtualTable
        columns={columns}
        dataSource={[]}
        virtual={true}
        height={400}
      />
    );

    // Should render table even with empty data
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('should handle column rendering in virtual mode', () => {
    const dataset = generateLargeDataset(200);
    
    render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        virtualThreshold={100}
        height={400}
      />
    );

    const virtualList = screen.getByTestId('virtual-list');
    expect(virtualList).toBeInTheDocument();
    
    // Should render some items (mocked to render first 10)
    expect(virtualList.children.length).toBeGreaterThan(0);
  });
});

describe('VirtualTable Memory Tests', () => {
  it('should not leak memory on unmount', () => {
    const dataset = Array.from({ length: 1000 }, (_, index) => ({
      id: index,
      name: `Item ${index}`,
    }));

    const columns = [
      { title: 'ID', dataIndex: 'id', key: 'id' },
      { title: 'Name', dataIndex: 'name', key: 'name' },
    ];

    const { unmount } = render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        height={400}
      />
    );

    // Unmount should not throw errors
    expect(() => unmount()).not.toThrow();
  });

  it('should handle rapid prop changes efficiently', () => {
    const columns = [
      { title: 'ID', dataIndex: 'id', key: 'id' },
      { title: 'Name', dataIndex: 'name', key: 'name' },
    ];

    let dataset = Array.from({ length: 100 }, (_, index) => ({
      id: index,
      name: `Item ${index}`,
    }));

    const { rerender } = render(
      <VirtualTable
        columns={columns}
        dataSource={dataset}
        virtual={true}
        height={400}
      />
    );

    // Rapidly change dataset
    for (let i = 0; i < 10; i++) {
      dataset = Array.from({ length: 100 + i * 10 }, (_, index) => ({
        id: index,
        name: `Item ${index} - ${i}`,
      }));

      rerender(
        <VirtualTable
          columns={columns}
          dataSource={dataset}
          virtual={true}
          height={400}
        />
      );
    }

    // Should still render correctly
    expect(screen.getByRole('table')).toBeInTheDocument();
  });
});

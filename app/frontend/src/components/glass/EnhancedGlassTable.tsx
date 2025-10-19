import React, { useState, useRef, useEffect } from 'react';
import { Table, TableProps, ConfigProvider } from 'antd';
import { ColumnsType } from 'antd/es/table';
import './EnhancedGlassTable.css';

export interface EnhancedGlassTableProps<T = any> extends TableProps<T> {
  /** 玻璃效果强度 */
  glassLevel?: 'sm' | 'md' | 'lg';
  /** 是否启用固定表头玻璃效果 */
  stickyHeader?: boolean;
  /** 是否启用行悬浮效果 */
  hoverEffect?: boolean;
  /** 是否禁用毛玻璃效果（兼容性降级） */
  disableGlass?: boolean;
  /** 自定义玻璃背景颜色 */
  glassColor?: string;
  /** 是否启用虚拟滚动（大数据集优化） */
  virtualScroll?: boolean;
}

const EnhancedGlassTable = <T extends Record<string, any>>({
  className = '',
  glassLevel = 'md',
  stickyHeader = true,
  hoverEffect = true,
  disableGlass = false,
  glassColor,
  virtualScroll = false,
  columns,
  dataSource,
  scroll,
  ...rest
}: EnhancedGlassTableProps<T>) => {
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout>();
  const tableRef = useRef<HTMLDivElement>(null);

  // 检测浏览器是否支持backdrop-filter
  const supportsBackdropFilter = () => {
    if (typeof window === 'undefined') return false;
    return CSS.supports('backdrop-filter', 'blur(1px)') || 
           CSS.supports('-webkit-backdrop-filter', 'blur(1px)');
  };

  const shouldUseGlass = !disableGlass && supportsBackdropFilter();

  // 处理滚动事件
  const handleScroll = () => {
    setIsScrolling(true);
    
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    scrollTimeoutRef.current = setTimeout(() => {
      setIsScrolling(false);
    }, 150);
  };

  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // 构建CSS类名
  const getTableClassName = () => {
    let baseClass = 'enhanced-glass-table';
    
    if (shouldUseGlass) {
      baseClass += ` glass-${glassLevel}`;
    } else {
      baseClass += ' glass-fallback';
    }
    
    if (stickyHeader) {
      baseClass += ' sticky-header';
    }
    
    if (hoverEffect) {
      baseClass += ' hover-effect';
    }
    
    if (isScrolling) {
      baseClass += ' scrolling';
    }
    
    if (virtualScroll) {
      baseClass += ' virtual-scroll';
    }
    
    return `${baseClass} ${className}`;
  };

  // 增强列配置
  const enhancedColumns: ColumnsType<T> = columns?.map(col => ({
    ...col,
    onHeaderCell: (column) => ({
      ...col.onHeaderCell?.(column),
      className: `glass-header-cell ${col.onHeaderCell?.(column)?.className || ''}`,
    }),
    onCell: (record, index) => ({
      ...col.onCell?.(record, index),
      className: `glass-body-cell ${col.onCell?.(record, index)?.className || ''}`,
    }),
  })) || [];

  // 自定义表格样式配置
  const tableTheme = {
    components: {
      Table: {
        headerBg: shouldUseGlass ? 'transparent' : 'rgba(255, 255, 255, 0.8)',
        headerColor: 'var(--neutral-text-primary)',
        rowHoverBg: shouldUseGlass ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.02)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        headerSplitColor: 'rgba(255, 255, 255, 0.1)',
      },
    },
  };

  // 处理大数据集的虚拟滚动
  const scrollConfig = virtualScroll ? {
    ...scroll,
    y: scroll?.y || 400,
  } : scroll;

  return (
    <div 
      ref={tableRef}
      className={getTableClassName()}
      style={{
        '--glass-color': glassColor || 'rgba(255, 255, 255, var(--glass-alpha-primary))',
      } as React.CSSProperties}
    >
      <ConfigProvider theme={tableTheme}>
        <Table<T>
          {...rest}
          columns={enhancedColumns}
          dataSource={dataSource}
          scroll={scrollConfig}
          onScroll={handleScroll}
          className="glass-table-inner"
          components={{
            header: {
              cell: (props: any) => (
                <th 
                  {...props} 
                  className={`glass-header-cell ${props.className || ''}`}
                />
              ),
            },
            body: {
              row: (props: any) => (
                <tr 
                  {...props} 
                  className={`glass-body-row ${props.className || ''}`}
                />
              ),
              cell: (props: any) => (
                <td 
                  {...props} 
                  className={`glass-body-cell ${props.className || ''}`}
                />
              ),
            },
          }}
        />
      </ConfigProvider>
      
      {/* 性能优化：滚动时显示简化样式 */}
      {isScrolling && shouldUseGlass && (
        <div className="scroll-performance-overlay" />
      )}
    </div>
  );
};

export default EnhancedGlassTable;

import React, { memo, useMemo, useCallback, useState, useRef, useEffect } from 'react';
import { Table, TableProps, Spin } from 'antd';
import { FixedSizeList as List } from 'react-window';
import { ColumnsType } from 'antd/es/table';

interface OptimizedTableProps<T> extends Omit<TableProps<T>, 'scroll'> {
  /** 是否启用虚拟滚动 */
  virtual?: boolean;
  /** 虚拟滚动的行高 */
  virtualRowHeight?: number;
  /** 虚拟滚动的容器高度 */
  virtualHeight?: number;
  /** 虚拟滚动阈值，超过此数量才启用虚拟滚动 */
  virtualThreshold?: number;
  /** 是否启用行选择优化 */
  optimizeSelection?: boolean;
  /** 是否启用列排序优化 */
  optimizeSorting?: boolean;
  /** 是否启用筛选优化 */
  optimizeFiltering?: boolean;
  /** 自定义空状态 */
  emptyComponent?: React.ReactNode;
  /** 加载状态 */
  loading?: boolean;
  /** 错误状态 */
  error?: string | null;
  /** 重试函数 */
  onRetry?: () => void;
}

// 虚拟化行组件
const VirtualRow: React.FC<{
  index: number;
  style: React.CSSProperties;
  data: {
    columns: ColumnsType<any>;
    dataSource: any[];
    rowKey: string | ((record: any) => string);
    onRow?: (record: any, index?: number) => React.HTMLAttributes<any>;
  };
}> = memo(({ index, style, data }) => {
  const { columns, dataSource, rowKey, onRow } = data;
  const record = dataSource[index];
  
  if (!record) return null;

  const key = typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
  const rowProps = onRow?.(record, index) || {};

  return (
    <div style={style} {...rowProps}>
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        {columns.map((column, colIndex) => {
          const { dataIndex, key: colKey, render, width } = column;
          const cellKey = colKey || (Array.isArray(dataIndex) ? dataIndex.join('.') : dataIndex) || colIndex;
          
          let cellValue = record;
          if (Array.isArray(dataIndex)) {
            cellValue = dataIndex.reduce((obj, key) => obj?.[key], record);
          } else if (dataIndex) {
            cellValue = record[dataIndex];
          }

          const renderedValue = render ? render(cellValue, record, index) : cellValue;

          return (
            <div
              key={cellKey}
              style={{
                width: width || 'auto',
                padding: '8px 16px',
                borderRight: '1px solid #f0f0f0',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {renderedValue}
            </div>
          );
        })}
      </div>
    </div>
  );
});

VirtualRow.displayName = 'VirtualRow';

// 优化的表格组件
function OptimizedTable<T extends Record<string, any>>({
  virtual = false,
  virtualRowHeight = 54,
  virtualHeight = 400,
  virtualThreshold = 100,
  optimizeSelection = true,
  optimizeSorting = true,
  optimizeFiltering = true,
  emptyComponent,
  loading = false,
  error = null,
  onRetry,
  dataSource = [],
  columns = [],
  rowKey = 'id',
  pagination,
  ...props
}: OptimizedTableProps<T>) {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [sortedInfo, setSortedInfo] = useState<any>({});
  const [filteredInfo, setFilteredInfo] = useState<any>({});
  const tableRef = useRef<HTMLDivElement>(null);

  // 判断是否应该使用虚拟滚动
  const shouldUseVirtual = useMemo(() => {
    return virtual && dataSource.length > virtualThreshold;
  }, [virtual, dataSource.length, virtualThreshold]);

  // 优化的列配置
  const optimizedColumns = useMemo(() => {
    return columns.map(column => {
      const optimizedColumn = { ...column };

      // 排序优化
      if (optimizeSorting && column.sorter) {
        optimizedColumn.sorter = typeof column.sorter === 'function' 
          ? column.sorter 
          : true;
        optimizedColumn.sortOrder = sortedInfo.columnKey === column.key ? sortedInfo.order : null;
      }

      // 筛选优化
      if (optimizeFiltering && column.filters) {
        optimizedColumn.filteredValue = filteredInfo[column.key as string] || null;
      }

      return optimizedColumn;
    });
  }, [columns, optimizeSorting, optimizeFiltering, sortedInfo, filteredInfo]);

  // 优化的数据源
  const optimizedDataSource = useMemo(() => {
    let result = [...dataSource];

    // 应用筛选
    if (optimizeFiltering) {
      Object.entries(filteredInfo).forEach(([key, values]) => {
        if (values && Array.isArray(values) && values.length > 0) {
          const column = columns.find(col => col.key === key);
          if (column && column.onFilter) {
            result = result.filter(record => 
              values.some(value => column.onFilter!(value, record))
            );
          }
        }
      });
    }

    // 应用排序
    if (optimizeSorting && sortedInfo.columnKey) {
      const column = columns.find(col => col.key === sortedInfo.columnKey);
      if (column && column.sorter && typeof column.sorter === 'function') {
        result.sort((a, b) => {
          const sortResult = column.sorter!(a, b, sortedInfo.order);
          return sortedInfo.order === 'descend' ? -sortResult : sortResult;
        });
      }
    }

    return result;
  }, [dataSource, columns, filteredInfo, sortedInfo, optimizeFiltering, optimizeSorting]);

  // 处理表格变化
  const handleChange = useCallback((pagination: any, filters: any, sorter: any) => {
    if (optimizeFiltering) {
      setFilteredInfo(filters);
    }
    if (optimizeSorting) {
      setSortedInfo(sorter);
    }
    props.onChange?.(pagination, filters, sorter);
  }, [optimizeFiltering, optimizeSorting, props]);

  // 处理行选择
  const rowSelection = useMemo(() => {
    if (!props.rowSelection) return undefined;

    const baseRowSelection = props.rowSelection;

    if (!optimizeSelection) return baseRowSelection;

    return {
      ...baseRowSelection,
      selectedRowKeys,
      onChange: (keys: React.Key[], rows: T[]) => {
        setSelectedRowKeys(keys);
        baseRowSelection.onChange?.(keys, rows);
      },
      onSelect: (record: T, selected: boolean, selectedRows: T[], nativeEvent: Event) => {
        baseRowSelection.onSelect?.(record, selected, selectedRows, nativeEvent);
      },
      onSelectAll: (selected: boolean, selectedRows: T[], changeRows: T[]) => {
        baseRowSelection.onSelectAll?.(selected, selectedRows, changeRows);
      },
    };
  }, [props.rowSelection, optimizeSelection, selectedRowKeys]);

  // 错误状态
  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{ color: '#ff4d4f', marginBottom: '16px' }}>
          {error}
        </div>
        {onRetry && (
          <button onClick={onRetry} style={{ padding: '8px 16px' }}>
            重试
          </button>
        )}
      </div>
    );
  }

  // 虚拟滚动表格
  if (shouldUseVirtual) {
    return (
      <div ref={tableRef} style={{ height: virtualHeight }}>
        <Spin spinning={loading}>
          {/* 表头 */}
          <div style={{ display: 'flex', background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
            {optimizedColumns.map((column, index) => (
              <div
                key={column.key || index}
                style={{
                  width: column.width || 'auto',
                  padding: '12px 16px',
                  fontWeight: 'bold',
                  borderRight: '1px solid #f0f0f0',
                }}
              >
                {column.title}
              </div>
            ))}
          </div>

          {/* 虚拟化内容 */}
          {optimizedDataSource.length > 0 ? (
            <List
              height={virtualHeight - 47} // 减去表头高度
              itemCount={optimizedDataSource.length}
              itemSize={virtualRowHeight}
              itemData={{
                columns: optimizedColumns,
                dataSource: optimizedDataSource,
                rowKey,
                onRow: props.onRow,
              }}
            >
              {VirtualRow}
            </List>
          ) : (
            <div style={{ textAlign: 'center', padding: '50px' }}>
              {emptyComponent || '暂无数据'}
            </div>
          )}
        </Spin>
      </div>
    );
  }

  // 普通表格
  return (
    <Table<T>
      {...props}
      columns={optimizedColumns}
      dataSource={optimizedDataSource}
      rowKey={rowKey}
      rowSelection={rowSelection}
      loading={loading}
      onChange={handleChange}
      pagination={pagination}
      locale={{
        emptyText: emptyComponent || '暂无数据',
      }}
    />
  );
}

// 使用memo优化
export default memo(OptimizedTable) as <T extends Record<string, any>>(
  props: OptimizedTableProps<T>
) => React.ReactElement;

// 导出类型
export type { OptimizedTableProps };

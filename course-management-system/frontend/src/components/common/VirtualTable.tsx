import React, { useMemo, CSSProperties } from 'react';
import { Table, TableProps } from 'antd';
import { FixedSizeList as List } from 'react-window';
import type { ListChildComponentProps } from 'react-window';

export interface VirtualTableProps<T = any> extends TableProps<T> {
  /** 虚拟滚动高度 */
  height?: number;
  /** 行高 */
  itemHeight?: number;
  /** 是否启用虚拟滚动 */
  virtual?: boolean;
  /** 虚拟滚动阈值，超过此数量才启用虚拟滚动 */
  virtualThreshold?: number;
}

// 虚拟滚动行组件
const VirtualTableRow = <T extends Record<string, any>>({
  data,
  index,
  style,
}: ListChildComponentProps & { data: { columns: any[]; dataSource: T[] } }) => {
  const { dataSource } = data;
  const item = dataSource[index];
  
  return (
    <tr style={style}>
      {data.columns.map((column, columnIndex) => {
        const key = column.dataIndex || column.key || columnIndex;
        const value = column.render ? column.render(item[key], item, index) : item[key];
        return (
          <td key={key} style={{ ...(column.width ? { width: column.width } : {}) }}>
            {value}
          </td>
        );
      })}
    </tr>
  );
};

const VirtualTable = <T extends Record<string, any>>({
  height = 400,
  itemHeight = 54,
  virtual = true,
  virtualThreshold = 100,
  dataSource = [],
  columns = [],
  ...props
}: VirtualTableProps<T>) => {
  // 判断是否需要启用虚拟滚动
  const shouldUseVirtual = useMemo(() => {
    return virtual && dataSource.length > virtualThreshold;
  }, [virtual, dataSource.length, virtualThreshold]);

  // 使用虚拟滚动渲染
  if (shouldUseVirtual) {
    const itemData = useMemo(() => ({ columns, dataSource }), [columns, dataSource]);
    
    return (
      <Table
        {...props}
        columns={columns}
        dataSource={[]}
        pagination={false}
        scroll={{ y: height }}
        components={{
          body: {
            wrapper: ({ className, style, ...restProps }) => (
              <List
                height={height}
                itemCount={dataSource.length}
                itemSize={itemHeight}
                itemData={itemData}
                style={{ ...style, overflow: 'auto' } as CSSProperties}
              >
                {VirtualTableRow}
              </List>
            ),
          },
        }}
      />
    );
  }

  // 使用普通表格渲染
  return (
    <Table
      {...props}
      columns={columns}
      dataSource={dataSource}
      scroll={{ y: height }}
    />
  );
};

export default React.memo(VirtualTable);
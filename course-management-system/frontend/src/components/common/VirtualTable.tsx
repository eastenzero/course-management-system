import React, { useMemo } from 'react';
import { Table, TableProps } from 'antd';

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

const VirtualTable = <T extends Record<string, any>>({
  height = 400,
  itemHeight = 54,
  virtual = true,
  virtualThreshold = 100,
  dataSource = [],
  ...props
}: VirtualTableProps<T>) => {
  // 判断是否需要启用虚拟滚动
  const shouldUseVirtual = useMemo(() => {
    return virtual && dataSource.length > virtualThreshold;
  }, [virtual, dataSource.length, virtualThreshold]);

  // 简化版虚拟滚动（暂时使用普通表格，等react-window安装完成后再启用）
  const shouldUseVirtualScrolling = false; // 暂时禁用虚拟滚动

  // 暂时使用普通表格，等react-window安装完成后再启用虚拟滚动
  return (
    <Table
      {...props}
      dataSource={dataSource}
      scroll={{ y: height }}
    />
  );
};

export default React.memo(VirtualTable);

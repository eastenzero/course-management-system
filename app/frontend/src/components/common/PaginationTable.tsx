import React, { useState, useEffect } from 'react';
import { Table, TableProps, Pagination, PaginationProps } from 'antd';

export interface PaginationTableProps<T = any> extends TableProps<T> {
  /** 总数据条数 */
  total?: number;
  /** 每页条数 */
  pageSize?: number;
  /** 当前页码 */
  current?: number;
  /** 分页配置 */
  paginationProps?: PaginationProps;
  /** 页面改变回调 */
  onPageChange?: (page: number, pageSize?: number) => void;
}

const PaginationTable = <T extends Record<string, any>>({
  total = 0,
  pageSize: defaultPageSize = 20,
  current: defaultCurrent = 1,
  paginationProps = {},
  onPageChange,
  ...props
}: PaginationTableProps<T>) => {
  const [current, setCurrent] = useState(defaultCurrent);
  const [pageSize, setPageSize] = useState(defaultPageSize);

  useEffect(() => {
    setCurrent(defaultCurrent);
  }, [defaultCurrent]);

  useEffect(() => {
    setPageSize(defaultPageSize);
  }, [defaultPageSize]);

  const handlePageChange: PaginationProps['onChange'] = (page, size) => {
    setCurrent(page);
    setPageSize(size || pageSize);
    onPageChange?.(page, size);
  };

  const paginationConfig: PaginationProps = {
    total,
    current,
    pageSize,
    onChange: handlePageChange,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条数据`,
    ...paginationProps,
  };

  return (
    <div>
      <Table {...props} pagination={false} />
      <div style={{ marginTop: '16px', textAlign: 'right' }}>
        <Pagination {...paginationConfig} />
      </div>
    </div>
  );
};

export default PaginationTable;
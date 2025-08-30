import React from 'react';
import { Table, Card, Space, Button, Input, Select, Tooltip } from 'antd';
import {
  ReloadOutlined,
  DownloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TableProps } from 'antd/es/table';
import type { TablePagination } from '../../types/index';
import './DataTable.css';

const { Option } = Select;

interface DataTableProps<T extends Record<string, any>>
  extends Omit<TableProps<T>, 'columns' | 'title'> {
  columns: ColumnsType<T>;
  dataSource: T[];
  loading?: boolean;
  pagination?: TablePagination | false;
  title?: string;
  subtitle?: string;
  showSearch?: boolean;
  showRefresh?: boolean;
  showExport?: boolean;
  showSettings?: boolean;
  searchPlaceholder?: string;
  searchValue?: string;
  onSearch?: (value: string) => void;
  onRefresh?: () => void;
  onExport?: () => void;
  onSettingsClick?: () => void;
  extraActions?: React.ReactNode;
  filters?: {
    key: string;
    label: string;
    options: { label: string; value: any }[];
    value?: any;
    onChange?: (value: any) => void;
  }[];
}

const DataTable = <T extends Record<string, any>>({
  columns,
  dataSource,
  loading = false,
  pagination,
  title,
  subtitle,
  showSearch = true,
  showRefresh = true,
  showExport = false,
  showSettings = false,
  searchPlaceholder = '搜索...',
  searchValue,
  onSearch,
  onRefresh,
  onExport,
  onSettingsClick,
  extraActions,
  filters,
  ...tableProps
}: DataTableProps<T>) => {
  const handleSearch = (value: string) => {
    onSearch?.(value);
  };

  const handleRefresh = () => {
    onRefresh?.();
  };

  const handleExport = () => {
    onExport?.();
  };

  const renderToolbar = () => {
    if (
      !showSearch &&
      !showRefresh &&
      !showExport &&
      !showSettings &&
      !extraActions &&
      !filters?.length
    ) {
      return null;
    }

    return (
      <div className="data-table-toolbar">
        <div className="toolbar-left">
          {showSearch && (
            <Input.Search
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={e => handleSearch(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              allowClear
            />
          )}

          {filters?.map(filter => (
            <Select
              key={filter.key}
              placeholder={filter.label}
              value={filter.value}
              onChange={filter.onChange}
              style={{ width: 150 }}
              allowClear
            >
              {filter.options.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          ))}
        </div>

        <div className="toolbar-right">
          <Space>
            {extraActions}

            {showRefresh && (
              <Tooltip title="刷新">
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  loading={loading}
                />
              </Tooltip>
            )}

            {showExport && (
              <Tooltip title="导出">
                <Button icon={<DownloadOutlined />} onClick={handleExport} />
              </Tooltip>
            )}

            {showSettings && (
              <Tooltip title="设置">
                <Button icon={<SettingOutlined />} onClick={onSettingsClick} />
              </Tooltip>
            )}
          </Space>
        </div>
      </div>
    );
  };

  const renderHeader = () => {
    if (!title && !subtitle) {
      return null;
    }

    return (
      <div className="data-table-header">
        {title && <h3 className="table-title">{title}</h3>}
        {subtitle && <p className="table-subtitle">{subtitle}</p>}
      </div>
    );
  };

  const defaultPagination = {
    current: 1,
    pageSize: 10,
    total: dataSource.length,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number, range: [number, number]) =>
      `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
  };

  const finalPagination =
    pagination === false
      ? false
      : {
          ...defaultPagination,
          ...pagination,
        };

  return (
    <Card className="data-table-card" bodyStyle={{ padding: 0 }}>
      {renderHeader()}
      {renderToolbar()}

      <div className="data-table-container">
        <Table<T>
          columns={columns}
          dataSource={dataSource}
          loading={loading}
          pagination={finalPagination}
          scroll={{ x: 'max-content' }}
          size="middle"
          className="data-table"
          {...tableProps}
        />
      </div>
    </Card>
  );
};

export default DataTable;

import React from 'react';
import { Button, Dropdown, MenuProps } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';

export interface ExportButtonProps {
  onExport: (format: 'csv' | 'excel' | 'json') => void;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const ExportButton: React.FC<ExportButtonProps> = ({
  onExport,
  loading = false,
  disabled = false,
  className,
  style,
}) => {
  const items: MenuProps['items'] = [
    {
      key: 'csv',
      label: '导出为CSV',
      onClick: () => onExport('csv'),
    },
    {
      key: 'excel',
      label: '导出为Excel',
      onClick: () => onExport('excel'),
    },
    {
      key: 'json',
      label: '导出为JSON',
      onClick: () => onExport('json'),
    },
  ];

  return (
    <Dropdown menu={{ items }} disabled={disabled || loading}>
      <Button
        icon={<DownloadOutlined />}
        loading={loading}
        disabled={disabled}
        className={className}
        style={style}
      >
        导出数据
      </Button>
    </Dropdown>
  );
};

export default ExportButton;
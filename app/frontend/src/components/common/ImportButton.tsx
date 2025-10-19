import React, { useRef } from 'react';
import { Button, message, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

export interface ImportButtonProps {
  onImport: (file: File) => Promise<void>;
  accept?: string;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const ImportButton: React.FC<ImportButtonProps> = ({
  onImport,
  accept = '.csv,.xlsx,.xls,.json',
  disabled = false,
  loading = false,
  className,
  style,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImport = async (file: File) => {
    try {
      await onImport(file);
      message.success('数据导入成功');
    } catch (error) {
      console.error('导入失败:', error);
      message.error('数据导入失败，请检查文件格式');
    }
  };

  const uploadProps: UploadProps = {
    beforeUpload: (file) => {
      handleImport(file);
      return false; // 阻止默认上传行为
    },
    showUploadList: false,
    accept,
    disabled: disabled || loading,
  };

  return (
    <Upload {...uploadProps}>
      <Button
        icon={<UploadOutlined />}
        loading={loading}
        disabled={disabled}
        className={className}
        style={style}
      >
        导入数据
      </Button>
    </Upload>
  );
};

export default ImportButton;
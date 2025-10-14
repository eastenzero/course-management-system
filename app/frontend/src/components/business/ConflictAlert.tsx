import React from 'react';
import { Alert, Button, Space } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

export interface ConflictAlertProps {
  conflicts: any[];
  onResolve: () => void;
  onIgnore: () => void;
  title?: string;
  description?: string;
}

const ConflictAlert: React.FC<ConflictAlertProps> = ({ 
  conflicts, 
  onResolve, 
  onIgnore,
  title = '检测到时间冲突',
  description
}) => {
  const conflictCount = conflicts.length;
  const defaultDescription = `发现 ${conflictCount} 个时间冲突，请及时处理`;

  return (
    <Alert
      message={title}
      description={description || defaultDescription}
      type="error"
      showIcon
      icon={<ExclamationCircleOutlined />}
      action={
        <Space>
          <Button size="small" type="primary" onClick={onResolve}>
            立即解决
          </Button>
          <Button size="small" onClick={onIgnore}>
            忽略
          </Button>
        </Space>
      }
    />
  );
};

export default ConflictAlert;
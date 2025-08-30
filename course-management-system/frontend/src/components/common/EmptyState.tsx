import React from 'react';
import { Empty, Button, Space } from 'antd';
import {
  InboxOutlined,
  FileSearchOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';

export interface EmptyStateProps {
  /** 空状态类型 */
  type?: 'empty' | 'search' | 'error' | 'loading';
  /** 自定义图标 */
  icon?: React.ReactNode;
  /** 主标题 */
  title?: string;
  /** 描述文本 */
  description?: string;
  /** 主要操作按钮 */
  primaryAction?: {
    text: string;
    onClick: () => void;
    icon?: React.ReactNode;
    type?: 'primary' | 'default';
  };
  /** 次要操作按钮 */
  secondaryAction?: {
    text: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
  /** 图片地址 */
  image?: string;
  /** 是否显示默认图片 */
  showImage?: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'empty',
  icon,
  title,
  description,
  primaryAction,
  secondaryAction,
  style,
  className,
  image,
  showImage = true,
}) => {
  // 根据类型获取默认配置
  const getDefaultConfig = () => {
    switch (type) {
      case 'search':
        return {
          icon: <FileSearchOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
          title: '没有找到相关内容',
          description: '请尝试调整搜索条件或关键词',
        };
      case 'error':
        return {
          icon: <ExclamationCircleOutlined style={{ fontSize: 64, color: '#ff4d4f' }} />,
          title: '加载失败',
          description: '数据加载出现问题，请稍后重试',
        };
      case 'loading':
        return {
          icon: <ReloadOutlined style={{ fontSize: 64, color: '#1890ff' }} spin />,
          title: '加载中...',
          description: '正在获取数据，请稍候',
        };
      default:
        return {
          icon: <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
          title: '暂无数据',
          description: '当前没有任何数据',
        };
    }
  };

  const defaultConfig = getDefaultConfig();
  const finalIcon = icon || defaultConfig.icon;
  const finalTitle = title || defaultConfig.title;
  const finalDescription = description || defaultConfig.description;

  // 渲染操作按钮
  const renderActions = () => {
    if (!primaryAction && !secondaryAction) return null;

    return (
      <Space>
        {secondaryAction && (
          <Button
            icon={secondaryAction.icon}
            onClick={secondaryAction.onClick}
          >
            {secondaryAction.text}
          </Button>
        )}
        {primaryAction && (
          <Button
            type={primaryAction.type || 'primary'}
            icon={primaryAction.icon}
            onClick={primaryAction.onClick}
          >
            {primaryAction.text}
          </Button>
        )}
      </Space>
    );
  };

  return (
    <div
      className={className}
      style={{
        padding: '40px 20px',
        textAlign: 'center',
        ...style,
      }}
    >
      <Empty
        image={showImage ? (image || Empty.PRESENTED_IMAGE_SIMPLE) : false}
        imageStyle={{
          height: showImage ? 60 : 0,
          marginBottom: showImage ? 16 : 0,
        }}
        description={
          <div>
            {!showImage && finalIcon && (
              <div style={{ marginBottom: 16 }}>
                {finalIcon}
              </div>
            )}
            <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
              {finalTitle}
            </div>
            <div style={{ color: '#999', fontSize: 14 }}>
              {finalDescription}
            </div>
          </div>
        }
      >
        {renderActions()}
      </Empty>
    </div>
  );
};

export default EmptyState;

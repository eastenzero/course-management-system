import React from 'react';
import { Card, Statistic, Progress, Space, Tag, Tooltip } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';

interface StatCardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: string;
  precision?: number;
  loading?: boolean;
  trend?: {
    value: number;
    isPositive: boolean;
    period?: string;
  };
  progress?: {
    percent: number;
    strokeColor?: string;
    showInfo?: boolean;
  };
  extra?: React.ReactNode;
  description?: string;
  tooltip?: string;
  status?: 'normal' | 'warning' | 'danger' | 'success';
  size?: 'default' | 'small';
  onClick?: () => void;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  prefix,
  suffix,
  precision,
  loading = false,
  trend,
  progress,
  extra,
  description,
  tooltip,
  status = 'normal',
  size = 'default',
  onClick,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return '#52c41a';
      case 'warning':
        return '#faad14';
      case 'danger':
        return '#ff4d4f';
      default:
        return '#1890ff';
    }
  };

  // const getStatusBorderColor = (status: string) => {
  //   switch (status) {
  //     case 'success':
  //       return '#b7eb8f';
  //     case 'warning':
  //       return '#ffe58f';
  //     case 'danger':
  //       return '#ffccc7';
  //     default:
  //       return '#91d5ff';
  //   }
  // };

  const cardStyle = {
    cursor: onClick ? 'pointer' : 'default',
    transition: 'all 0.3s ease',
    borderLeft: `4px solid ${getStatusColor(status)}`,
    ...(onClick && {
      '&:hover': {
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        transform: 'translateY(-2px)',
      },
    }),
  };

  const bodyStyle = {
    padding: size === 'small' ? '16px' : '24px',
  };

  return (
    <Card
      style={cardStyle}
      bodyStyle={bodyStyle}
      loading={loading}
      onClick={onClick}
      hoverable={!!onClick}
    >
      <div style={{ position: 'relative' }}>
        {/* 标题行 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: size === 'small' ? '8px' : '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ 
              fontSize: size === 'small' ? '13px' : '14px',
              color: '#666',
              fontWeight: '500'
            }}>
              {title}
            </span>
            {tooltip && (
              <Tooltip title={tooltip}>
                <InfoCircleOutlined 
                  style={{ 
                    marginLeft: '4px', 
                    color: '#999',
                    fontSize: '12px'
                  }} 
                />
              </Tooltip>
            )}
          </div>
          {extra && (
            <div>{extra}</div>
          )}
        </div>

        {/* 主要数值 */}
        <div style={{ marginBottom: size === 'small' ? '8px' : '12px' }}>
          <Statistic
            value={value}
            prefix={prefix}
            suffix={suffix}
            precision={precision}
            valueStyle={{
              fontSize: size === 'small' ? '20px' : '24px',
              fontWeight: 'bold',
              color: getStatusColor(status),
            }}
          />
        </div>

        {/* 趋势指示器 */}
        {trend && (
          <div style={{ marginBottom: '8px' }}>
            <Space size="small">
              <span style={{
                color: trend.isPositive ? '#52c41a' : '#ff4d4f',
                fontSize: '12px',
                fontWeight: '500',
              }}>
                {trend.isPositive ? (
                  <ArrowUpOutlined />
                ) : (
                  <ArrowDownOutlined />
                )}
                {Math.abs(trend.value)}%
              </span>
              {trend.period && (
                <span style={{ fontSize: '12px', color: '#999' }}>
                  {trend.period}
                </span>
              )}
            </Space>
          </div>
        )}

        {/* 进度条 */}
        {progress && (
          <div style={{ marginBottom: '8px' }}>
            <Progress
              percent={progress.percent}
              strokeColor={progress.strokeColor || getStatusColor(status)}
              showInfo={progress.showInfo !== false}
              size="small"
            />
          </div>
        )}

        {/* 描述文字 */}
        {description && (
          <div style={{
            fontSize: '12px',
            color: '#666',
            lineHeight: '1.4',
            marginTop: '8px',
          }}>
            {description}
          </div>
        )}

        {/* 状态标签 */}
        {status !== 'normal' && (
          <div style={{ 
            position: 'absolute',
            top: '0',
            right: '0',
          }}>
            <Tag 
              color={getStatusColor(status)}
              style={{ 
                margin: 0,
                fontSize: '10px',
                padding: '2px 6px',
                borderRadius: '0 0 0 8px',
              }}
            >
              {status === 'success' && '良好'}
              {status === 'warning' && '注意'}
              {status === 'danger' && '警告'}
            </Tag>
          </div>
        )}
      </div>
    </Card>
  );
};

export default StatCard;

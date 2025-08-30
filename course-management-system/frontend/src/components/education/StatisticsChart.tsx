import React from 'react';
import { Card, Row, Col, Statistic, Progress, Typography, Empty } from 'antd';
import {
  TrophyOutlined,
  UserOutlined,
  BookOutlined,
  BarChartOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

export interface StatisticsData {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: string;
  precision?: number;
  valueStyle?: React.CSSProperties;
  trend?: {
    value: number;
    isPositive: boolean;
    label: string;
  };
}

export interface ChartData {
  name: string;
  value: number;
  color?: string;
  percentage?: number;
}

export interface StatisticsChartProps {
  title?: string;
  statistics?: StatisticsData[];
  chartData?: ChartData[];
  chartType?: 'bar' | 'pie' | 'progress';
  showTrend?: boolean;
  loading?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const StatisticsChart: React.FC<StatisticsChartProps> = ({
  title,
  statistics = [],
  chartData = [],
  chartType = 'progress',
  showTrend = false,
  loading = false,
  className,
  style
}) => {
  const renderStatistics = () => {
    if (statistics.length === 0) return null;

    return (
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {statistics.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.prefix}
                suffix={stat.suffix}
                precision={stat.precision}
                valueStyle={stat.valueStyle}
              />
              {showTrend && stat.trend && (
                <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center' }}>
                  {stat.trend.isPositive ? (
                    <RiseOutlined style={{ color: '#52c41a', marginRight: '4px' }} />
                  ) : (
                    <FallOutlined style={{ color: '#ff4d4f', marginRight: '4px' }} />
                  )}
                  <Text 
                    style={{ 
                      color: stat.trend.isPositive ? '#52c41a' : '#ff4d4f',
                      fontSize: '12px'
                    }}
                  >
                    {stat.trend.value}% {stat.trend.label}
                  </Text>
                </div>
              )}
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  const renderProgressChart = () => {
    if (chartData.length === 0) return null;

    return (
      <div>
        {chartData.map((item, index) => (
          <div key={index} style={{ marginBottom: '16px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              marginBottom: '8px' 
            }}>
              <Text>{item.name}</Text>
              <Text strong>{item.value}</Text>
            </div>
            <Progress
              percent={item.percentage || (item.value / Math.max(...chartData.map(d => d.value))) * 100}
              strokeColor={item.color}
              showInfo={false}
            />
          </div>
        ))}
      </div>
    );
  };

  const renderBarChart = () => {
    if (chartData.length === 0) return null;

    const maxValue = Math.max(...chartData.map(d => d.value));

    return (
      <div style={{ display: 'flex', alignItems: 'end', height: '200px', gap: '8px' }}>
        {chartData.map((item, index) => {
          const height = (item.value / maxValue) * 160;
          return (
            <div key={index} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              flex: 1
            }}>
              <Text style={{ fontSize: '12px', marginBottom: '4px' }}>
                {item.value}
              </Text>
              <div
                style={{
                  width: '100%',
                  height: `${height}px`,
                  backgroundColor: item.color || '#1890ff',
                  borderRadius: '4px 4px 0 0',
                  minHeight: '4px'
                }}
              />
              <Text 
                style={{ 
                  fontSize: '12px', 
                  marginTop: '8px',
                  textAlign: 'center',
                  wordBreak: 'break-all'
                }}
              >
                {item.name}
              </Text>
            </div>
          );
        })}
      </div>
    );
  };

  const renderPieChart = () => {
    if (chartData.length === 0) return null;

    const total = chartData.reduce((sum, item) => sum + item.value, 0);

    return (
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          {/* 简单的饼图表示 - 使用圆形进度条 */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              width: '120px', 
              height: '120px', 
              margin: '0 auto',
              position: 'relative'
            }}>
              {chartData.map((item, index) => {
                const percentage = (item.value / total) * 100;
                return (
                  <Progress
                    key={index}
                    type="circle"
                    percent={percentage}
                    size={120 - index * 20}
                    strokeColor={item.color}
                    trailColor="transparent"
                    format={() => ''}
                    style={{
                      position: 'absolute',
                      top: index * 10,
                      left: index * 10
                    }}
                  />
                );
              })}
            </div>
          </div>
        </Col>
        <Col xs={24} md={12}>
          <div>
            {chartData.map((item, index) => (
              <div key={index} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                marginBottom: '8px' 
              }}>
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    backgroundColor: item.color || '#1890ff',
                    borderRadius: '2px',
                    marginRight: '8px'
                  }}
                />
                <Text style={{ flex: 1 }}>{item.name}</Text>
                <Text strong>{item.value}</Text>
                <Text type="secondary" style={{ marginLeft: '8px' }}>
                  ({((item.value / total) * 100).toFixed(1)}%)
                </Text>
              </div>
            ))}
          </div>
        </Col>
      </Row>
    );
  };

  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return renderBarChart();
      case 'pie':
        return renderPieChart();
      case 'progress':
      default:
        return renderProgressChart();
    }
  };

  const hasData = statistics.length > 0 || chartData.length > 0;

  return (
    <Card 
      title={title}
      loading={loading}
      className={className}
      style={style}
    >
      {!hasData ? (
        <Empty
          description="暂无统计数据"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <>
          {renderStatistics()}
          {chartData.length > 0 && (
            <div>
              {title && statistics.length > 0 && (
                <Title level={5} style={{ marginBottom: '16px' }}>
                  <BarChartOutlined style={{ marginRight: '8px' }} />
                  数据分布
                </Title>
              )}
              {renderChart()}
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default StatisticsChart;

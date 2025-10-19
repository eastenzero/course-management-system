import React, { useEffect, useState } from 'react';
import { Card, Badge, Progress, Typography, Space, Tooltip, Alert } from 'antd';
import { 
  ThunderboltOutlined, 
  EyeOutlined, 
  WifiOutlined,
  DesktopOutlined,
  ClockCircleOutlined 
} from '@ant-design/icons';
import { 
  useAccessibility, 
  usePerformance, 
  useContrastCheck 
} from '../../hooks/useAccessibilityAndPerformance';
import { useTheme } from '../../hooks/useThemeV2';

const { Text, Title } = Typography;

interface PerformanceMetrics {
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

const PerformanceMonitor: React.FC = () => {
  const { prefersReducedMotion, announce } = useAccessibility();
  const { networkQuality } = usePerformance();
  const { getThemeColors } = useTheme();
  const themeColors = getThemeColors();

  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    lcp: 0,
    fid: 0,
    cls: 0,
    ttfb: 0
  });

  const [memoryUsage, setMemoryUsage] = useState<{
    used: number;
    total: number;
    percentage: number;
  }>({ used: 0, total: 0, percentage: 0 });

  // 检查主题色彩对比度
  const { ratio: primaryContrast, passesAA: primaryPassesAA } = useContrastCheck(
    themeColors?.primary || '#1890ff',
    '#ffffff'
  );

  useEffect(() => {
    // 监控Web Vitals
    if ('PerformanceObserver' in window) {
      // Largest Contentful Paint
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          setMetrics(prev => ({ ...prev, lcp: entry.startTime }));
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // First Input Delay
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          setMetrics(prev => ({ ...prev, fid: (entry as any).processingStart - entry.startTime }));
        }
      }).observe({ entryTypes: ['first-input'] });

      // Cumulative Layout Shift
      new PerformanceObserver((entryList) => {
        let clsValue = 0;
        for (const entry of entryList.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        setMetrics(prev => ({ ...prev, cls: clsValue }));
      }).observe({ entryTypes: ['layout-shift'] });
    }

    // 监控内存使用
    const monitorMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const used = memory.usedJSHeapSize / 1048576; // MB
        const total = memory.totalJSHeapSize / 1048576; // MB
        const percentage = (used / total) * 100;
        
        setMemoryUsage({ used, total, percentage });
        
        // 内存使用过高时警告
        if (percentage > 80) {
          announce('内存使用率过高，可能影响性能', 'assertive');
        }
      }
    };

    const interval = setInterval(monitorMemory, 5000);
    monitorMemory(); // 立即执行一次

    return () => clearInterval(interval);
  }, [announce]);

  const getScoreColor = (value: number, thresholds: { good: number; fair: number }) => {
    if (value <= thresholds.good) return '#52c41a';
    if (value <= thresholds.fair) return '#faad14';
    return '#ff4d4f';
  };

  const getNetworkIcon = () => {
    switch (networkQuality) {
      case 'fast': return <WifiOutlined style={{ color: '#52c41a' }} />;
      case 'slow': return <WifiOutlined style={{ color: '#ff4d4f' }} />;
      default: return <WifiOutlined style={{ color: '#faad14' }} />;
    }
  };

  return (
    <div style={{ padding: '16px', maxWidth: '800px' }}>
      <Title level={4}>
        <ThunderboltOutlined /> 性能与无障碍监控
      </Title>

      {/* 总体状态 */}
      <Alert
        message="系统状态"
        description={
          <Space>
            <Badge 
              status={primaryPassesAA ? 'success' : 'error'} 
              text={`对比度: ${primaryContrast.toFixed(2)} ${primaryPassesAA ? '(通过AA)' : '(未通过AA)'}`} 
            />
            <Badge 
              status={prefersReducedMotion ? 'processing' : 'default'} 
              text={prefersReducedMotion ? '减少动效模式' : '标准动效模式'} 
            />
            <Badge 
              status={networkQuality === 'fast' ? 'success' : networkQuality === 'slow' ? 'error' : 'warning'} 
              text={`网络: ${networkQuality}`} 
            />
          </Space>
        }
        type="info"
        showIcon
        style={{ marginBottom: '16px' }}
      />

      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* Web Vitals */}
        <Card title="Core Web Vitals" size="small">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <Tooltip title="最大内容绘制时间 (应 ≤ 2.5s)">
                <Text strong>LCP</Text>
              </Tooltip>
              <div style={{ marginTop: '8px' }}>
                <Progress
                  percent={Math.min((metrics.lcp / 2500) * 100, 100)}
                  strokeColor={getScoreColor(metrics.lcp, { good: 2500, fair: 4000 })}
                  format={() => `${(metrics.lcp / 1000).toFixed(2)}s`}
                />
              </div>
            </div>

            <div>
              <Tooltip title="首次输入延迟 (应 ≤ 100ms)">
                <Text strong>FID</Text>
              </Tooltip>
              <div style={{ marginTop: '8px' }}>
                <Progress
                  percent={Math.min((metrics.fid / 100) * 100, 100)}
                  strokeColor={getScoreColor(metrics.fid, { good: 100, fair: 300 })}
                  format={() => `${metrics.fid.toFixed(1)}ms`}
                />
              </div>
            </div>

            <div>
              <Tooltip title="累积布局偏移 (应 ≤ 0.1)">
                <Text strong>CLS</Text>
              </Tooltip>
              <div style={{ marginTop: '8px' }}>
                <Progress
                  percent={Math.min((metrics.cls / 0.1) * 100, 100)}
                  strokeColor={getScoreColor(metrics.cls, { good: 0.1, fair: 0.25 })}
                  format={() => metrics.cls.toFixed(3)}
                />
              </div>
            </div>
          </div>
        </Card>

        {/* 系统资源 */}
        <Card 
          title={
            <Space>
              <DesktopOutlined />
              <span>系统资源</span>
            </Space>
          } 
          size="small"
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            <div>
              <Text strong>内存使用</Text>
              <div style={{ marginTop: '8px' }}>
                <Progress
                  percent={memoryUsage.percentage}
                  strokeColor={memoryUsage.percentage > 80 ? '#ff4d4f' : '#52c41a'}
                  format={() => `${memoryUsage.used.toFixed(1)} / ${memoryUsage.total.toFixed(1)} MB`}
                />
              </div>
            </div>

            <div>
              <Text strong>网络质量</Text>
              <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getNetworkIcon()}
                <Text>{networkQuality === 'fast' ? '快速' : networkQuality === 'slow' ? '慢速' : '未知'}</Text>
              </div>
            </div>
          </div>
        </Card>

        {/* 无障碍检查 */}
        <Card 
          title={
            <Space>
              <EyeOutlined />
              <span>无障碍检查</span>
            </Space>
          } 
          size="small"
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <Text strong>主题色对比度</Text>
              <div style={{ marginTop: '8px' }}>
                <Badge 
                  status={primaryPassesAA ? 'success' : 'error'} 
                  text={`${primaryContrast.toFixed(2)}:1`} 
                />
                <div style={{ marginTop: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {primaryPassesAA ? '✓ 通过 WCAG AA' : '✗ 未通过 WCAG AA'}
                  </Text>
                </div>
              </div>
            </div>

            <div>
              <Text strong>动效偏好</Text>
              <div style={{ marginTop: '8px' }}>
                <Badge 
                  status={prefersReducedMotion ? 'processing' : 'success'} 
                  text={prefersReducedMotion ? '减少动效' : '正常动效'} 
                />
                <div style={{ marginTop: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {prefersReducedMotion ? '⚡ 性能优化模式' : '🎨 完整视觉效果'}
                  </Text>
                </div>
              </div>
            </div>

            <div>
              <Text strong>键盘导航</Text>
              <div style={{ marginTop: '8px' }}>
                <Badge status="success" text="已启用" />
                <div style={{ marginTop: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    ⌨️ 支持Tab键导航
                  </Text>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* 优化建议 */}
        {(memoryUsage.percentage > 70 || metrics.lcp > 2500 || !primaryPassesAA) && (
          <Card title="优化建议" size="small">
            <Space direction="vertical">
              {memoryUsage.percentage > 70 && (
                <Alert
                  message="内存使用率较高"
                  description="建议关闭不必要的标签页或刷新页面"
                  type="warning"
                  showIcon
                />
              )}
              {metrics.lcp > 2500 && (
                <Alert
                  message="页面加载较慢"
                  description="尝试关闭其他应用程序或检查网络连接"
                  type="warning"
                  showIcon
                />
              )}
              {!primaryPassesAA && (
                <Alert
                  message="色彩对比度不足"
                  description="当前主题色彩可能影响视力障碍用户的使用体验"
                  type="error"
                  showIcon
                />
              )}
            </Space>
          </Card>
        )}
      </Space>
    </div>
  );
};

export default PerformanceMonitor;
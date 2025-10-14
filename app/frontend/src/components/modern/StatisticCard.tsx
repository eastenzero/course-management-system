import React, { useEffect, useState } from 'react';
import { Card } from 'antd';
import '../../styles/modern.css';

interface StatisticCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  variant: 'courses' | 'students' | 'grades' | 'tasks';
  suffix?: string;
  precision?: number;
  onClick?: () => void;
  loading?: boolean;
}

const StatisticCard: React.FC<StatisticCardProps> = ({
  title,
  value,
  icon,
  variant,
  suffix = '',
  precision = 0,
  onClick,
  loading = false
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  // 数字动画效果
  useEffect(() => {
    if (loading) return;
    
    setIsAnimating(true);
    const duration = 800; // 动画持续时间
    const steps = 60; // 动画步数
    const increment = value / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current = Math.min(increment * step, value);
      setDisplayValue(current);

      if (step >= steps) {
        clearInterval(timer);
        setDisplayValue(value);
        setIsAnimating(false);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value, loading]);

  const formatValue = (val: number) => {
    if (precision > 0) {
      return val.toFixed(precision);
    }
    return Math.floor(val).toString();
  };

  const getCardClass = () => {
    return `stat-card stat-card-${variant} ${onClick ? 'hover-lift' : ''} optimized-animation`;
  };

  return (
    <Card
      className={getCardClass()}
      onClick={onClick}
      loading={loading}
      style={{ 
        cursor: onClick ? 'pointer' : 'default',
        border: 'none',
        height: '140px'
      }}
      bodyStyle={{ 
        padding: 0,
        height: '100%',
        position: 'relative'
      }}
    >
      <div className="stat-icon">
        {icon}
      </div>
      <div className="stat-content">
        <div className="stat-value">
          {formatValue(displayValue)}{suffix}
        </div>
        <div className="stat-label">{title}</div>
      </div>
      
      {/* 装饰性浮动元素 */}
      <div className="floating-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>
      
      {/* 加载状态覆盖层 */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(255, 255, 255, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 'var(--border-radius-lg)'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            borderTop: '2px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        </div>
      )}
    </Card>
  );
};

export default StatisticCard;

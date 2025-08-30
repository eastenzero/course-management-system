import React from 'react';
import { Card, CardProps } from 'antd';
import './GlassCard.css';

interface GlassCardProps extends Omit<CardProps, 'className'> {
  variant?: 'primary' | 'secondary' | 'accent';
  hoverable?: boolean;
  glassEffect?: 'strong' | 'medium' | 'light';
  className?: string;
  loading?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  variant = 'primary',
  hoverable = true,
  glassEffect = 'medium',
  className = '',
  loading = false,
  children,
  ...props
}) => {
  const glassClasses = [
    'glass-card',
    `glass-card--${variant}`,
    `glass-effect--${glassEffect}`,
    hoverable ? 'glass-hover' : '',
    loading ? 'glass-loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <Card
      className={glassClasses}
      bordered={false}
      loading={loading}
      {...props}
    >
      {children}
    </Card>
  );
};

export default GlassCard;

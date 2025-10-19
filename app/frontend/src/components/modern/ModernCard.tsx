import React from 'react';
import { Card, CardProps } from 'antd';
import '../../styles/modern.css';

interface ModernCardProps extends CardProps {
  variant?: 'default' | 'glass' | 'elevated';
  hoverable?: boolean;
  animated?: boolean;
}

const ModernCard: React.FC<ModernCardProps> = ({
  variant = 'default',
  hoverable = true,
  animated = true,
  className = '',
  children,
  ...props
}) => {
  const getCardClass = () => {
    let classes = 'modern-card';
    
    if (hoverable) {
      classes += ' hover-lift';
    }
    
    if (animated) {
      classes += ' optimized-animation fade-in';
    }
    
    if (className) {
      classes += ` ${className}`;
    }
    
    return classes;
  };

  const getCardStyle = () => {
    const baseStyle = {
      border: 'none',
      ...props.style
    };

    switch (variant) {
      case 'glass':
        return {
          ...baseStyle,
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
        };
      case 'elevated':
        return {
          ...baseStyle,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        };
      default:
        return baseStyle;
    }
  };

  return (
    <Card
      {...props}
      className={getCardClass()}
      style={getCardStyle()}
    >
      {children}
    </Card>
  );
};

export default ModernCard;

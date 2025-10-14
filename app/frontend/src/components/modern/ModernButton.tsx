import React from 'react';
import { Button, ButtonProps } from 'antd';
import '../../styles/modern.css';

interface ModernButtonProps extends ButtonProps {
  variant?: 'teacher' | 'student' | 'default';
  gradient?: boolean;
}

const ModernButton: React.FC<ModernButtonProps> = ({
  variant = 'default',
  gradient = true,
  className = '',
  children,
  ...props
}) => {
  const getButtonClass = () => {
    let classes = 'modern-button optimized-animation';
    
    if (gradient) {
      if (variant === 'student') {
        classes += ' student-style';
      }
      // teacher style is default
    }
    
    if (className) {
      classes += ` ${className}`;
    }
    
    return classes;
  };

  return (
    <Button
      {...props}
      className={getButtonClass()}
    >
      {children}
    </Button>
  );
};

export default ModernButton;

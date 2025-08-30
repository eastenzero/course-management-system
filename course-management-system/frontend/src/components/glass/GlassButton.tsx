import React from 'react';
import { Button, ButtonProps } from 'antd';
import classNames from 'classnames';
import './GlassButton.css';

export interface GlassButtonProps extends Omit<ButtonProps, 'className'> {
  /** 玻璃效果强度 */
  glassEffect?: 'light' | 'medium' | 'strong';
  /** 按钮变体 */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** 是否启用悬浮效果 */
  hoverable?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 是否启用按压效果 */
  pressable?: boolean;
}

const GlassButton: React.FC<GlassButtonProps> = ({
  glassEffect = 'medium',
  variant = 'primary',
  hoverable = true,
  pressable = true,
  className,
  children,
  ...props
}) => {
  const buttonClassName = classNames(
    'glass-button',
    `glass-button--${variant}`,
    `glass-button--effect-${glassEffect}`,
    {
      'glass-button--hoverable': hoverable,
      'glass-button--pressable': pressable,
    },
    className
  );

  return (
    <Button
      {...props}
      className={buttonClassName}
    >
      {children}
    </Button>
  );
};

export default GlassButton;

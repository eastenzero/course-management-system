import React from 'react';
import { Input, InputProps } from 'antd';
import classNames from 'classnames';
import './GlassInput.css';

export interface GlassInputProps extends Omit<InputProps, 'className'> {
  /** 玻璃效果强度 */
  glassEffect?: 'light' | 'medium' | 'strong';
  /** 输入框变体 */
  variant?: 'default' | 'filled' | 'outlined';
  /** 自定义类名 */
  className?: string;
  /** 是否显示聚焦高光 */
  focusHighlight?: boolean;
}

const GlassInput: React.FC<GlassInputProps> = ({
  glassEffect = 'medium',
  variant = 'default',
  focusHighlight = true,
  className,
  ...props
}) => {
  const inputClassName = classNames(
    'glass-input',
    `glass-input--${variant}`,
    `glass-input--effect-${glassEffect}`,
    {
      'glass-input--focus-highlight': focusHighlight,
    },
    className
  );

  return (
    <Input
      {...props}
      className={inputClassName}
    />
  );
};

// TextArea 组件
export interface GlassTextAreaProps extends Omit<React.ComponentProps<typeof Input.TextArea>, 'className'> {
  glassEffect?: 'light' | 'medium' | 'strong';
  variant?: 'default' | 'filled' | 'outlined';
  className?: string;
  focusHighlight?: boolean;
}

const GlassTextArea: React.FC<GlassTextAreaProps> = ({
  glassEffect = 'medium',
  variant = 'default',
  focusHighlight = true,
  className,
  ...props
}) => {
  const textAreaClassName = classNames(
    'glass-input',
    'glass-textarea',
    `glass-input--${variant}`,
    `glass-input--effect-${glassEffect}`,
    {
      'glass-input--focus-highlight': focusHighlight,
    },
    className
  );

  return (
    <Input.TextArea
      {...props}
      className={textAreaClassName}
    />
  );
};

// Password 组件
export interface GlassPasswordProps extends Omit<React.ComponentProps<typeof Input.Password>, 'className'> {
  glassEffect?: 'light' | 'medium' | 'strong';
  variant?: 'default' | 'filled' | 'outlined';
  className?: string;
  focusHighlight?: boolean;
}

const GlassPassword: React.FC<GlassPasswordProps> = ({
  glassEffect = 'medium',
  variant = 'default',
  focusHighlight = true,
  className,
  ...props
}) => {
  const passwordClassName = classNames(
    'glass-input',
    `glass-input--${variant}`,
    `glass-input--effect-${glassEffect}`,
    {
      'glass-input--focus-highlight': focusHighlight,
    },
    className
  );

  return (
    <Input.Password
      {...props}
      className={passwordClassName}
    />
  );
};

// Search 组件
export interface GlassSearchProps extends Omit<React.ComponentProps<typeof Input.Search>, 'className'> {
  glassEffect?: 'light' | 'medium' | 'strong';
  variant?: 'default' | 'filled' | 'outlined';
  className?: string;
  focusHighlight?: boolean;
}

const GlassSearch: React.FC<GlassSearchProps> = ({
  glassEffect = 'medium',
  variant = 'default',
  focusHighlight = true,
  className,
  ...props
}) => {
  const searchClassName = classNames(
    'glass-input',
    `glass-input--${variant}`,
    `glass-input--effect-${glassEffect}`,
    {
      'glass-input--focus-highlight': focusHighlight,
    },
    className
  );

  return (
    <Input.Search
      {...props}
      className={searchClassName}
    />
  );
};

// 组合导出
GlassInput.TextArea = GlassTextArea;
GlassInput.Password = GlassPassword;
GlassInput.Search = GlassSearch;

export default GlassInput;

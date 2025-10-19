import React, { useEffect, useState } from 'react';
import { Modal, ModalProps, ConfigProvider } from 'antd';
import './EnhancedGlassModal.css';

export interface EnhancedGlassModalProps extends ModalProps {
  /** 玻璃效果强度 */
  glassLevel?: 'sm' | 'md' | 'lg';
  /** 是否启用背景模糊 */
  backgroundBlur?: boolean;
  /** 是否禁用毛玻璃效果（兼容性降级） */
  disableGlass?: boolean;
  /** 自定义玻璃背景颜色 */
  glassColor?: string;
  /** 进入动画类型 */
  enterAnimation?: 'fade' | 'scale' | 'slide';
  /** 是否启用噪点纹理 */
  enableNoise?: boolean;
}

const EnhancedGlassModal: React.FC<EnhancedGlassModalProps> = ({
  children,
  className = '',
  glassLevel = 'md',
  backgroundBlur = true,
  disableGlass = false,
  glassColor,
  enterAnimation = 'scale',
  enableNoise = true,
  open,
  onCancel,
  ...rest
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [animationClass, setAnimationClass] = useState('');

  // 检测浏览器是否支持backdrop-filter
  const supportsBackdropFilter = () => {
    if (typeof window === 'undefined') return false;
    return CSS.supports('backdrop-filter', 'blur(1px)') || 
           CSS.supports('-webkit-backdrop-filter', 'blur(1px)');
  };

  const shouldUseGlass = !disableGlass && supportsBackdropFilter();

  // 处理Modal显示/隐藏动画
  useEffect(() => {
    if (open) {
      setIsVisible(true);
      // 延迟添加动画类，确保DOM已渲染
      setTimeout(() => {
        setAnimationClass(`enter-${enterAnimation}`);
      }, 10);
    } else {
      setAnimationClass(`exit-${enterAnimation}`);
      // 延迟隐藏，等待动画完成
      setTimeout(() => {
        setIsVisible(false);
      }, 200);
    }
  }, [open, enterAnimation]);

  // 构建CSS类名
  const getModalClassName = () => {
    let baseClass = 'enhanced-glass-modal';
    
    if (shouldUseGlass) {
      baseClass += ` glass-${glassLevel}`;
    } else {
      baseClass += ' glass-fallback';
    }
    
    if (backgroundBlur) {
      baseClass += ' background-blur';
    }
    
    if (enableNoise && shouldUseGlass) {
      baseClass += ' glass-noise';
    }
    
    if (animationClass) {
      baseClass += ` ${animationClass}`;
    }
    
    return `${baseClass} ${className}`;
  };

  // 构建遮罩层类名
  const getMaskClassName = () => {
    let maskClass = 'enhanced-glass-mask';
    
    if (backgroundBlur && shouldUseGlass) {
      maskClass += ' mask-blur';
    } else {
      maskClass += ' mask-fallback';
    }
    
    return maskClass;
  };

  // 自定义Modal样式配置
  const modalTheme = {
    components: {
      Modal: {
        contentBg: 'transparent',
        headerBg: 'transparent',
        footerBg: 'transparent',
        borderRadiusLG: parseInt(getComputedStyle(document.documentElement)
          .getPropertyValue('--radius-modal').replace('px', '')) || 20,
      },
    },
  };

  // 处理ESC键关闭
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && open && onCancel) {
        onCancel(event as any);
      }
    };

    if (open) {
      document.addEventListener('keydown', handleEscape);
      // 防止背景滚动
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [open, onCancel]);

  return (
    <ConfigProvider theme={modalTheme}>
      <Modal
        {...rest}
        open={isVisible}
        onCancel={onCancel}
        className={getModalClassName()}
        maskClassName={getMaskClassName()}
        destroyOnClose
        centered
        styles={{
          mask: {
            backdropFilter: backgroundBlur && shouldUseGlass ? 'blur(var(--blur-sm))' : 'none',
          },
          content: {
            '--glass-color': glassColor || 'rgba(255, 255, 255, var(--glass-alpha-primary))',
            ...rest.style,
          } as React.CSSProperties,
        }}
        // 禁用默认动画，使用自定义动画
        transitionName=""
        maskTransitionName=""
      >
        <div className="glass-modal-content">
          {children}
        </div>
      </Modal>
    </ConfigProvider>
  );
};

export default EnhancedGlassModal;

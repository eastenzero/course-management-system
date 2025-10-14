import React from 'react';
import { ArrowRightOutlined } from '@ant-design/icons';
import '../../styles/modern.css';

interface QuickActionButtonProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'accent';
  disabled?: boolean;
  loading?: boolean;
}

const QuickActionButton: React.FC<QuickActionButtonProps> = ({ 
  icon, 
  title, 
  description, 
  onClick, 
  variant = 'primary',
  disabled = false,
  loading = false
}) => {
  const handleClick = () => {
    if (!disabled && !loading) {
      onClick();
    }
  };

  return (
    <button 
      className={`quick-action-btn ${variant} ${disabled ? 'disabled' : ''} ${loading ? 'loading' : ''} fade-in`}
      onClick={handleClick}
      disabled={disabled || loading}
      style={{
        opacity: disabled ? 0.6 : 1,
        cursor: disabled || loading ? 'not-allowed' : 'pointer'
      }}
    >
      <div className="btn-icon">
        {loading ? (
          <div style={{
            width: '24px',
            height: '24px',
            border: '2px solid #e0e0e0',
            borderTop: '2px solid #667eea',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        ) : (
          icon
        )}
      </div>
      <div className="btn-content">
        <div className="btn-title">{title}</div>
        <div className="btn-description">{description}</div>
      </div>
      <div className="btn-arrow">
        <ArrowRightOutlined />
      </div>
    </button>
  );
};

// 快速操作按钮组
interface QuickActionsProps {
  actions: Array<{
    key: string;
    icon: React.ReactNode;
    title: string;
    description: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary' | 'accent';
    disabled?: boolean;
    loading?: boolean;
  }>;
  title?: string;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ 
  actions, 
  title = '快速操作' 
}) => {
  return (
    <div className="modern-card fade-in" style={{ padding: '24px' }}>
      <h3 style={{ 
        marginBottom: '20px', 
        fontSize: '18px', 
        fontWeight: 600,
        color: '#262626'
      }}>
        {title}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
        {actions.map((action, index) => (
          <div 
            key={action.key}
            style={{
              animationDelay: `${index * 0.1}s`
            }}
          >
            <QuickActionButton
              icon={action.icon}
              title={action.title}
              description={action.description}
              onClick={action.onClick}
              variant={action.variant}
              disabled={action.disabled}
              loading={action.loading}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuickActionButton;

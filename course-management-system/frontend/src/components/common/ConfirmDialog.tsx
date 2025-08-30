import React from 'react';
import ReactDOM from 'react-dom';
import { Modal, Button, Space } from 'antd';
import {
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';

export interface ConfirmDialogProps {
  /** 是否显示对话框 */
  visible: boolean;
  /** 关闭对话框回调 */
  onClose: () => void;
  /** 确认回调 */
  onConfirm: () => void | Promise<void>;
  /** 取消回调 */
  onCancel?: () => void;
  /** 对话框标题 */
  title?: string;
  /** 对话框内容 */
  content?: React.ReactNode;
  /** 对话框类型 */
  type?: 'info' | 'success' | 'warning' | 'error' | 'confirm';
  /** 确认按钮文本 */
  okText?: string;
  /** 取消按钮文本 */
  cancelText?: string;
  /** 确认按钮类型 */
  okType?: 'primary' | 'default';
  /** 是否显示取消按钮 */
  showCancel?: boolean;
  /** 是否加载中 */
  loading?: boolean;
  /** 对话框宽度 */
  width?: number | string;
  /** 是否可以通过点击遮罩关闭 */
  maskClosable?: boolean;
  /** 自定义图标 */
  icon?: React.ReactNode;
  /** 是否居中显示 */
  centered?: boolean;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  visible,
  onClose,
  onConfirm,
  onCancel,
  title,
  content,
  type = 'confirm',
  okText = '确定',
  cancelText = '取消',
  okType,
  showCancel = true,
  loading = false,
  width = 416,
  maskClosable = false,
  icon,
  centered = true,
}) => {
  // 根据类型获取默认配置
  const getTypeConfig = () => {
    switch (type) {
      case 'info':
        return {
          icon: <InfoCircleOutlined style={{ color: '#1890ff' }} />,
          title: '信息',
          okType: 'primary' as const,
        };
      case 'success':
        return {
          icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
          title: '成功',
          okType: 'primary' as const,
        };
      case 'warning':
        return {
          icon: <WarningOutlined style={{ color: '#faad14' }} />,
          title: '警告',
          okType: 'primary' as const,
        };
      case 'error':
        return {
          icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
          title: '错误',
          okType: 'primary' as const,
        };
      default:
        return {
          icon: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
          title: '确认',
          okType: 'primary' as const,
        };
    }
  };

  const typeConfig = getTypeConfig();
  const finalIcon = icon !== undefined ? icon : typeConfig.icon;
  const finalTitle = title || typeConfig.title;
  const finalOkType = okType || typeConfig.okType;

  const handleConfirm = async () => {
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      // 如果确认操作失败，不关闭对话框
      console.error('Confirm action failed:', error);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    onClose();
  };

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={width}
      maskClosable={maskClosable}
      centered={centered}
      destroyOnClose
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        {finalIcon && (
          <div style={{ fontSize: 22, marginTop: 2 }}>
            {finalIcon}
          </div>
        )}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
            {finalTitle}
          </div>
          {content && (
            <div style={{ color: '#666', lineHeight: 1.6, marginBottom: 16 }}>
              {content}
            </div>
          )}
          <div style={{ textAlign: 'right' }}>
            <Space>
              {showCancel && (
                <Button onClick={handleCancel} disabled={loading}>
                  {cancelText}
                </Button>
              )}
              <Button
                type={finalOkType}
                onClick={handleConfirm}
                loading={loading}
              >
                {okText}
              </Button>
            </Space>
          </div>
        </div>
      </div>
    </Modal>
  );
};

// 便捷方法
export const showConfirm = (props: Omit<ConfirmDialogProps, 'visible' | 'onClose'>) => {
  return new Promise<boolean>((resolve) => {
    const div = document.createElement('div');
    document.body.appendChild(div);

    const destroy = () => {
      const unmountResult = ReactDOM.unmountComponentAtNode(div);
      if (unmountResult && div.parentNode) {
        div.parentNode.removeChild(div);
      }
    };

    const onConfirm = async () => {
      try {
        if (props.onConfirm) {
          await props.onConfirm();
        }
        resolve(true);
        destroy();
      } catch (error) {
        console.error('Confirm failed:', error);
      }
    };

    const onCancel = () => {
      if (props.onCancel) {
        props.onCancel();
      }
      resolve(false);
      destroy();
    };

    const ConfirmComponent = () => (
      <ConfirmDialog
        {...props}
        visible={true}
        onClose={onCancel}
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    );

    ReactDOM.render(<ConfirmComponent />, div);
  });
};

export default ConfirmDialog;

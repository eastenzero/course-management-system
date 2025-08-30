import React, { useState } from 'react';
import {
  Typography,
  Card,
  Form,
  Input,
  Button,
  message,
  Space,
  Alert,
  Progress,
  Row,
  Col,
} from 'antd';
import {
  LockOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  SafetyOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { authAPI } from '../../services/api';

const { Title } = Typography;

interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

const PasswordChangePage: React.FC = () => {
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [newPassword, setNewPassword] = useState('');

  // 密码强度检测
  const getPasswordStrength = (password: string): { score: number; text: string; color: string } => {
    if (!password) return { score: 0, text: '', color: '' };

    let score = 0;
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      numbers: /\d/.test(password),
      symbols: /[^A-Za-z0-9]/.test(password),
    };

    score = Object.values(checks).filter(Boolean).length;

    if (score <= 2) return { score: score * 20, text: '弱', color: '#ff4d4f' };
    if (score <= 3) return { score: score * 20, text: '中等', color: '#faad14' };
    if (score <= 4) return { score: score * 20, text: '强', color: '#52c41a' };
    return { score: 100, text: '很强', color: '#52c41a' };
  };

  const passwordStrength = getPasswordStrength(newPassword);

  const handleSubmit = async (values: PasswordFormData) => {
    try {
      setSubmitting(true);
      
      // 调用API修改密码
      await authAPI.changePassword({
        current_password: values.currentPassword,
        new_password: values.newPassword
      });
      
      message.success('密码修改成功，请重新登录');
      form.resetFields();
      setNewPassword('');
      
      // 可以在这里跳转到登录页面
      // navigate('/login');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '密码修改失败，请重试';
      message.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const validateCurrentPassword = async (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入当前密码'));
    }
    // TODO: 这里可以添加当前密码验证逻辑
    return Promise.resolve();
  };

  const validateNewPassword = async (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入新密码'));
    }
    if (value.length < 8) {
      return Promise.reject(new Error('密码长度至少8位'));
    }
    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(value)) {
      return Promise.reject(new Error('密码必须包含字母和数字'));
    }
    return Promise.resolve();
  };

  const validateConfirmPassword = async (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请确认新密码'));
    }
    if (value !== form.getFieldValue('newPassword')) {
      return Promise.reject(new Error('两次输入的密码不一致'));
    }
    return Promise.resolve();
  };

  return (
    <div className="password-change-page">
      <div className="page-header">
        <Title level={2}>修改密码</Title>
        <p>为了账户安全，请定期更换密码</p>
      </div>

      <Row gutter={24}>
        <Col xs={24} lg={16}>
          <Card title="修改密码" icon={<LockOutlined />}>
            <Alert
              message="密码安全提示"
              description={
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  <li>密码长度至少8位</li>
                  <li>必须包含字母和数字</li>
                  <li>建议包含大小写字母、数字和特殊字符</li>
                  <li>不要使用容易被猜到的密码</li>
                  <li>定期更换密码，建议3-6个月更换一次</li>
                </ul>
              }
              type="info"
              showIcon
              style={{ marginBottom: '24px' }}
            />

            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              autoComplete="off"
            >
              <Form.Item
                name="currentPassword"
                label="当前密码"
                rules={[{ validator: validateCurrentPassword }]}
              >
                <Input.Password
                  placeholder="请输入当前密码"
                  prefix={<LockOutlined />}
                  iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              <Form.Item
                name="newPassword"
                label="新密码"
                rules={[{ validator: validateNewPassword }]}
              >
                <Input.Password
                  placeholder="请输入新密码"
                  prefix={<LockOutlined />}
                  iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </Form.Item>

              {newPassword && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <span style={{ fontSize: '14px', color: '#666' }}>密码强度：</span>
                    <span style={{ color: passwordStrength.color, fontWeight: 'bold' }}>
                      {passwordStrength.text}
                    </span>
                  </div>
                  <Progress
                    percent={passwordStrength.score}
                    strokeColor={passwordStrength.color}
                    showInfo={false}
                    size="small"
                  />
                </div>
              )}

              <Form.Item
                name="confirmPassword"
                label="确认新密码"
                dependencies={['newPassword']}
                rules={[{ validator: validateConfirmPassword }]}
              >
                <Input.Password
                  placeholder="请再次输入新密码"
                  prefix={<LockOutlined />}
                  iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={submitting}
                  icon={<SafetyOutlined />}
                  size="large"
                >
                  修改密码
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="安全建议" size="small">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                  强密码特征
                </div>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#666' }}>
                  <li>长度8位以上</li>
                  <li>包含大小写字母</li>
                  <li>包含数字</li>
                  <li>包含特殊字符</li>
                </ul>
              </div>

              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                  <SafetyOutlined style={{ color: '#1890ff', marginRight: '8px' }} />
                  安全提醒
                </div>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#666' }}>
                  <li>不要在多个网站使用相同密码</li>
                  <li>不要将密码告诉他人</li>
                  <li>定期更换密码</li>
                  <li>使用密码管理器</li>
                </ul>
              </div>

              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                  <LockOutlined style={{ color: '#faad14', marginRight: '8px' }} />
                  避免使用
                </div>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#666' }}>
                  <li>生日、姓名等个人信息</li>
                  <li>连续数字或字母</li>
                  <li>常见密码（123456等）</li>
                  <li>键盘排列（qwerty等）</li>
                </ul>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PasswordChangePage;

import React, { useEffect } from 'react';
import { Card, Button, Space, Typography, Row, Col, message } from 'antd';
import { BgColorsOutlined } from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';

const { Title, Text } = Typography;

const ThemeTestPage: React.FC = () => {
  const { uiTheme, setUITheme, toggleMode, getThemeColors } = useTheme();

  // 测试主题切换
  const testThemeSwitch = (category: 'monet' | 'morandi', key: 'a' | 'b' | 'c') => {
    console.log('切换主题:', category, key);
    setUITheme(category, key);
    message.success(`已切换到 ${category} - ${key}`);
  };

  // 获取当前主题颜色
  const currentColors = getThemeColors();

  useEffect(() => {
    console.log('当前主题状态:', uiTheme);
    console.log('当前主题颜色:', currentColors);

    // 显示localStorage中的主题数据
    try {
      const savedTheme = localStorage.getItem('ui-theme-v2');
      console.log('localStorage中的主题:', savedTheme ? JSON.parse(savedTheme) : '无');
    } catch (error) {
      console.warn('读取localStorage失败:', error);
    }
  }, [uiTheme, currentColors]);

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>主题切换测试页面</Title>
      
      {/* 当前主题信息 */}
      <Card title="当前主题信息" style={{ marginBottom: '24px' }}>
        <Space direction="vertical">
          <Text>类别: {uiTheme.category}</Text>
          <Text>主题键: {uiTheme.themeKey}</Text>
          <Text>模式: {uiTheme.mode}</Text>
          {currentColors && (
            <div>
              <Text>主色: </Text>
              <span 
                style={{ 
                  display: 'inline-block',
                  width: '20px',
                  height: '20px',
                  backgroundColor: currentColors.primary,
                  marginRight: '8px',
                  border: '1px solid #ccc'
                }}
              />
              <Text>{currentColors.primary}</Text>
            </div>
          )}
        </Space>
      </Card>

      {/* 主题切换按钮 */}
      <Card title="主题切换测试" style={{ marginBottom: '24px' }}>
        <Title level={4}>莫奈主题</Title>
        <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
          <Col>
            <Button 
              type={uiTheme.category === 'monet' && uiTheme.themeKey === 'a' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('monet', 'a')}
            >
              莫奈 A (清晨湖畔)
            </Button>
          </Col>
          <Col>
            <Button 
              type={uiTheme.category === 'monet' && uiTheme.themeKey === 'b' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('monet', 'b')}
            >
              莫奈 B (晨曦花园)
            </Button>
          </Col>
          <Col>
            <Button 
              type={uiTheme.category === 'monet' && uiTheme.themeKey === 'c' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('monet', 'c')}
            >
              莫奈 C (海风薰衣草)
            </Button>
          </Col>
        </Row>

        <Title level={4}>莫兰迪主题</Title>
        <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
          <Col>
            <Button 
              type={uiTheme.category === 'morandi' && uiTheme.themeKey === 'a' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('morandi', 'a')}
            >
              莫兰迪 A (岩石与苔)
            </Button>
          </Col>
          <Col>
            <Button 
              type={uiTheme.category === 'morandi' && uiTheme.themeKey === 'b' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('morandi', 'b')}
            >
              莫兰迪 B (燕麦与石墨)
            </Button>
          </Col>
          <Col>
            <Button 
              type={uiTheme.category === 'morandi' && uiTheme.themeKey === 'c' ? 'primary' : 'default'}
              onClick={() => testThemeSwitch('morandi', 'c')}
            >
              莫兰迪 C (陶瓷与灰烬)
            </Button>
          </Col>
        </Row>

        <Title level={4}>模式切换</Title>
        <Button onClick={toggleMode} icon={<BgColorsOutlined />}>
          切换到 {uiTheme.mode === 'light' ? '深色' : '浅色'} 模式
        </Button>

        <Title level={4}>存储管理</Title>
        <Space>
          <Button
            onClick={() => {
              localStorage.removeItem('ui-theme-v2');
              message.success('已清除主题缓存，刷新页面将生成新的随机主题');
            }}
          >
            清除主题缓存
          </Button>
          <Button
            onClick={() => {
              const saved = localStorage.getItem('ui-theme-v2');
              message.info(saved ? `当前缓存: ${saved}` : '无缓存数据');
            }}
          >
            查看缓存
          </Button>
        </Space>
      </Card>

      {/* CSS变量显示 */}
      <Card title="CSS变量检查">
        <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          <div>--color-primary: <span style={{ color: 'var(--color-primary)' }}>var(--color-primary)</span></div>
          <div>--color-secondary: <span style={{ color: 'var(--color-secondary)' }}>var(--color-secondary)</span></div>
          <div>--color-tertiary: <span style={{ color: 'var(--color-tertiary)' }}>var(--color-tertiary)</span></div>
          <div>--color-accent: <span style={{ color: 'var(--color-accent)' }}>var(--color-accent)</span></div>
        </div>
      </Card>

      {/* 样式测试区域 */}
      <Card title="样式效果测试">
        <div 
          style={{
            padding: '20px',
            background: 'var(--color-primary)',
            color: 'white',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px'
          }}
        >
          主色背景测试区域
        </div>
        <div 
          style={{
            padding: '20px',
            background: 'var(--color-secondary)',
            color: 'white',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px'
          }}
        >
          辅色背景测试区域
        </div>
        <div 
          style={{
            padding: '20px',
            background: 'var(--color-accent)',
            color: 'white',
            borderRadius: 'var(--radius-md)'
          }}
        >
          强调色背景测试区域
        </div>
      </Card>
    </div>
  );
};

export default ThemeTestPage;

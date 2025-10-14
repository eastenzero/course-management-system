import React from 'react';
import { Card, Row, Col, Typography, Switch, Space, Tooltip } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';
import { monetThemes, morandiThemes, type UIThemeCategory, type UIThemeKey } from '../../styles/design-tokens-v2';
import './SimpleThemeSelector.css';

const { Text } = Typography;

interface SimpleThemeSelectorProps {
  onClose?: () => void;
}

const SimpleThemeSelector: React.FC<SimpleThemeSelectorProps> = ({ onClose }) => {
  const { uiTheme, setUITheme, toggleMode } = useTheme();

  // 主题选项配置
  const themeOptions = [
    {
      category: 'monet' as UIThemeCategory,
      name: '莫奈印象派',
      description: '水彩柔光，活泼亲和',
      themes: [
        { key: 'a' as UIThemeKey, name: '清晨湖畔', colors: monetThemes.a },
        { key: 'b' as UIThemeKey, name: '晨曦花园', colors: monetThemes.b },
        { key: 'c' as UIThemeKey, name: '海风薰衣草', colors: monetThemes.c },
      ]
    },
    {
      category: 'morandi' as UIThemeCategory,
      name: '莫兰迪色系',
      description: '静谧克制，专业稳重',
      themes: [
        { key: 'a' as UIThemeKey, name: '岩石与苔', colors: morandiThemes.a },
        { key: 'b' as UIThemeKey, name: '燕麦与石墨', colors: morandiThemes.b },
        { key: 'c' as UIThemeKey, name: '陶瓷与灰烬', colors: morandiThemes.c },
      ]
    }
  ];

  // 处理主题选择
  const handleThemeSelect = (category: UIThemeCategory, themeKey: UIThemeKey) => {
    console.log('点击主题选择:', { category, themeKey });
    console.log('当前主题:', uiTheme);
    console.log('setUITheme函数:', setUITheme);

    try {
      setUITheme(category, themeKey);
      console.log('主题切换成功:', { category, themeKey });
    } catch (error) {
      console.error('主题切换失败:', error);
    }
  };

  // 处理模式切换
  const handleModeToggle = (checked: boolean) => {
    console.log('点击模式切换:', checked);
    console.log('当前模式:', uiTheme.mode);

    try {
      toggleMode();
      console.log('模式切换成功');
    } catch (error) {
      console.error('模式切换失败:', error);
    }
  };

  return (
    <Card 
      className="simple-theme-selector"
      title="主题设置"
      size="small"
      style={{ width: 400, maxHeight: 500, overflow: 'auto' }}
    >
      {/* 明暗模式切换 */}
      <div className="mode-section">
        <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
          <Text strong>显示模式</Text>
          <Space>
            <SunOutlined />
            <Switch
              checked={uiTheme.mode === 'dark'}
              onChange={handleModeToggle}
              size="small"
            />
            <MoonOutlined />
          </Space>
        </Space>
      </div>

      {/* 主题选择 */}
      {themeOptions.map(categoryOption => (
        <div key={categoryOption.category} className="theme-category-section">
          <div className="category-header">
            <Text strong>{categoryOption.name}</Text>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
              {categoryOption.description}
            </Text>
          </div>
          
          <Row gutter={[8, 8]} style={{ marginTop: '8px' }}>
            {categoryOption.themes.map(theme => {
              const isActive = uiTheme.category === categoryOption.category && uiTheme.themeKey === theme.key;
              
              return (
                <Col span={8} key={theme.key}>
                  <Tooltip title={theme.name}>
                    <div
                      className={`theme-option ${isActive ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('主题选项被点击:', theme.name);
                        handleThemeSelect(categoryOption.category, theme.key);
                      }}
                      style={{
                        cursor: 'pointer',
                        userSelect: 'none',
                        pointerEvents: 'auto'
                      }}
                    >
                      <div 
                        className="theme-preview"
                        style={{ 
                          background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})` 
                        }}
                      >
                        {isActive && <div className="active-indicator">✓</div>}
                      </div>
                      <Text className="theme-name">{theme.name}</Text>
                      <div className="color-dots">
                        <div 
                          className="color-dot" 
                          style={{ backgroundColor: theme.colors.primary }}
                        />
                        <div 
                          className="color-dot" 
                          style={{ backgroundColor: theme.colors.secondary }}
                        />
                        <div 
                          className="color-dot" 
                          style={{ backgroundColor: theme.colors.accent }}
                        />
                      </div>
                    </div>
                  </Tooltip>
                </Col>
              );
            })}
          </Row>
        </div>
      ))}

      {/* 当前主题信息 */}
      <div className="current-theme-info">
        <Text type="secondary" style={{ fontSize: '12px' }}>
          当前: {themeOptions.find(cat => cat.category === uiTheme.category)?.name} - {
            themeOptions
              .find(cat => cat.category === uiTheme.category)
              ?.themes.find(t => t.key === uiTheme.themeKey)?.name
          } ({uiTheme.mode === 'dark' ? '深色' : '浅色'})
        </Text>
      </div>
    </Card>
  );
};

export default SimpleThemeSelector;

import React, { useState } from 'react';
import { 
  Drawer, 
  Button, 
  Space, 
  Typography, 
  Card, 
  Row, 
  Col, 
  Switch, 
  Divider,
  Tooltip,
  Badge
} from 'antd';
import { 
  SettingOutlined, 
  BgColorsOutlined, 
  SunOutlined, 
  MoonOutlined,
  CheckOutlined
} from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';
import { monetThemes, morandiThemes } from '../../styles/design-tokens-v2';
import type { UIThemeCategory, UIThemeKey } from '../../hooks/useThemeV2';
import './ThemeSelector.css';

const { Title, Text } = Typography;

interface ThemePreviewProps {
  category: UIThemeCategory;
  themeKey: UIThemeKey;
  isSelected: boolean;
  onClick: () => void;
}

const ThemePreview: React.FC<ThemePreviewProps> = ({ 
  category, 
  themeKey, 
  isSelected, 
  onClick 
}) => {
  const themes = category === 'monet' ? monetThemes : morandiThemes;
  const theme = themes[themeKey as keyof typeof themes] as any;
  
  if (!theme) {
    return null;
  }
  
  return (
    <Card
      className={`theme-preview ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      hoverable
      size="small"
      bodyStyle={{ padding: '12px' }}
    >
      <div className="theme-preview-header">
        <Text strong>{theme.name}</Text>
        {isSelected && <CheckOutlined className="selected-icon" />}
      </div>
      
      <div className="theme-preview-colors">
        <div 
          className="color-swatch primary" 
          style={{ backgroundColor: theme.primary }}
          title="主色"
        />
        <div 
          className="color-swatch secondary" 
          style={{ backgroundColor: theme.secondary }}
          title="辅色"
        />
        <div 
          className="color-swatch tertiary" 
          style={{ backgroundColor: theme.tertiary }}
          title="点缀色"
        />
        <div 
          className="color-swatch accent" 
          style={{ backgroundColor: theme.accent }}
          title="强调色"
        />
      </div>
      
      <div className="theme-preview-demo">
        <div 
          className="demo-card"
          style={{
            background: `linear-gradient(135deg, ${theme.primary}20, ${theme.secondary}20)`,
            border: `1px solid ${theme.primary}40`,
            borderRadius: '8px'
          }}
        >
          <div className="demo-content">
            <div 
              className="demo-button"
              style={{ backgroundColor: theme.primary }}
            />
            <div className="demo-text-lines">
              <div className="demo-line" style={{ backgroundColor: theme.accent }} />
              <div className="demo-line short" style={{ backgroundColor: theme.tertiary }} />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

const ThemeSelector: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const { uiTheme, setUITheme, toggleMode } = useTheme();

  const handleThemeSelect = (category: UIThemeCategory, themeKey: UIThemeKey) => {
    setUITheme(category, themeKey);
  };

  const renderThemeCategory = (category: UIThemeCategory, title: string, description: string) => {
    const themes = category === 'monet' ? monetThemes : morandiThemes;
    
    return (
      <div className="theme-category">
        <div className="category-header">
          <Title level={4}>{title}</Title>
          <Text type="secondary">{description}</Text>
        </div>
        
        <Row gutter={[12, 12]}>
          {Object.entries(themes).map(([key, theme]) => (
            <Col span={12} key={key}>
              <ThemePreview
                category={category}
                themeKey={key as UIThemeKey}
                isSelected={uiTheme.category === category && uiTheme.themeKey === key}
                onClick={() => handleThemeSelect(category, key as UIThemeKey)}
              />
            </Col>
          ))}
        </Row>
      </div>
    );
  };

  return (
    <>
      <Tooltip title="主题设置">
        <Button
          type="text"
          icon={<BgColorsOutlined />}
          onClick={() => setVisible(true)}
          className="theme-selector-trigger"
        />
      </Tooltip>

      <Drawer
        title={
          <Space>
            <SettingOutlined />
            <span>主题设置</span>
          </Space>
        }
        placement="right"
        width={400}
        open={visible}
        onClose={() => setVisible(false)}
        className="theme-selector-drawer"
      >
        <div className="theme-selector-content">
          {/* 明暗模式切换 */}
          <Card size="small" className="mode-selector">
            <div className="mode-selector-header">
              <Title level={5}>显示模式</Title>
              <Switch
                checked={uiTheme.mode === 'dark'}
                onChange={toggleMode}
                checkedChildren={<MoonOutlined />}
                unCheckedChildren={<SunOutlined />}
              />
            </div>
            <Text type="secondary">
              {uiTheme.mode === 'dark' ? '深色模式' : '浅色模式'}
            </Text>
          </Card>

          <Divider />

          {/* 莫奈主题 */}
          {renderThemeCategory(
            'monet',
            '莫奈主题',
            '水彩柔光、空气感、淡高光'
          )}

          <Divider />

          {/* 莫兰迪主题 */}
          {renderThemeCategory(
            'morandi',
            '莫兰迪主题',
            '低饱和灰调、静谧克制'
          )}

          <Divider />

          {/* 当前主题信息 */}
          <Card size="small" className="current-theme-info">
            <Title level={5}>当前主题</Title>
            <Space direction="vertical" size="small">
              <Text>
                <Badge 
                  color={uiTheme.category === 'monet' ? '#A9D6E5' : '#A3B18A'} 
                  text={uiTheme.category === 'monet' ? '莫奈系列' : '莫兰迪系列'}
                />
              </Text>
              <Text>
                主题：{uiTheme.category === 'monet' 
                  ? monetThemes[uiTheme.themeKey as keyof typeof monetThemes]?.name
                  : morandiThemes[uiTheme.themeKey as keyof typeof morandiThemes]?.name
                }
              </Text>
              <Text>模式：{uiTheme.mode === 'dark' ? '深色' : '浅色'}</Text>
            </Space>
          </Card>

          {/* 使用说明 */}
          <Card size="small" className="theme-guide">
            <Title level={5}>使用建议</Title>
            <Space direction="vertical" size="small">
              <Text type="secondary">• 教师端推荐使用莫兰迪主题，更专业稳重</Text>
              <Text type="secondary">• 学生端推荐使用莫奈主题，更活泼友好</Text>
              <Text type="secondary">• 深色模式适合长时间使用，保护视力</Text>
            </Space>
          </Card>
        </div>
      </Drawer>
    </>
  );
};

export default ThemeSelector;

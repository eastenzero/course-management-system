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
  Badge,
  message
} from 'antd';
import { 
  SettingOutlined, 
  BgColorsOutlined, 
  SunOutlined, 
  MoonOutlined,
  CheckOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';
import { monetThemes, morandiThemes, type UIThemeCategory, type UIThemeKey } from '../../styles/design-tokens-v2';
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
  const theme = themes[themeKey];
  
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

const EnhancedThemeSelector: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const { uiTheme, setUITheme, toggleMode, userRole } = useTheme();

  const handleThemeSelect = (category: UIThemeCategory, themeKey: UIThemeKey) => {
    setUITheme(category, themeKey);
    const themes = category === 'monet' ? monetThemes : morandiThemes;
    const themeName = themes[themeKey]?.name || themeKey;
    message.success(`已切换到${category === 'monet' ? '莫奈' : '莫兰迪'}主题 - ${themeName}`);
  };

  const renderThemeCategory = (category: UIThemeCategory, title: string, description: string) => {
    const themes = category === 'monet' ? monetThemes : morandiThemes;
    const isRecommended = (category === 'morandi' && userRole === 'teacher') || 
                         (category === 'monet' && userRole === 'student');
    
    return (
      <div className="theme-category">
        <div className="category-header">
          <Space>
            <Title level={4}>{title}</Title>
            {isRecommended && <Badge count="推荐" style={{ backgroundColor: '#52c41a' }} />}
          </Space>
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
          className="theme-selector-trigger glass-surface"
          style={{
            borderRadius: 'var(--radius-button)',
            backdropFilter: 'blur(var(--blur-sm))',
          }}
        />
      </Tooltip>

      <Drawer
        title={
          <Space>
            <AppstoreOutlined />
            <span>主题与外观</span>
          </Space>
        }
        placement="right"
        width={420}
        open={visible}
        onClose={() => setVisible(false)}
        className="enhanced-theme-selector-drawer"
        styles={{
          body: { padding: '24px' }
        }}
      >
        <div className="theme-selector-content">
          {/* 当前主题信息 */}
          <Card size="small" className="current-theme-info glass-surface-secondary">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text type="secondary">当前主题</Text>
                <br />
                <Text strong>
                  {uiTheme.category === 'monet' ? '莫奈' : '莫兰迪'} - {
                    (uiTheme.category === 'monet' ? monetThemes : morandiThemes)[uiTheme.themeKey]?.name || uiTheme.themeKey
                  }
                </Text>
              </div>
              <div>
                <Text type="secondary">显示模式</Text>
                <br />
                <Space>
                  <Text>{uiTheme.mode === 'dark' ? '深色模式' : '浅色模式'}</Text>
                  <Switch
                    checked={uiTheme.mode === 'dark'}
                    onChange={toggleMode}
                    checkedChildren={<MoonOutlined />}
                    unCheckedChildren={<SunOutlined />}
                    size="small"
                  />
                </Space>
              </div>
            </Space>
          </Card>

          <Divider />

          {/* 用户角色推荐 */}
          {userRole && (
            <>
              <Card size="small" className="role-recommendation">
                <Space>
                  <SettingOutlined />
                  <div>
                    <Text strong>角色推荐</Text>
                    <br />
                    <Text type="secondary">
                      {userRole === 'teacher' 
                        ? '教师端推荐使用莫兰迪主题，提供专业稳重的视觉体验'
                        : '学生端推荐使用莫奈主题，营造轻松活泼的学习氛围'
                      }
                    </Text>
                  </div>
                </Space>
              </Card>
              <Divider />
            </>
          )}

          {/* 莫奈主题 */}
          {renderThemeCategory(
            'monet',
            '莫奈主题系列',
            '水彩柔光、空气感、淡高光的现代美学'
          )}

          <Divider />

          {/* 莫兰迪主题 */}
          {renderThemeCategory(
            'morandi',
            '莫兰迪主题系列',
            '低饱和灰调、静谧克制的经典美学'
          )}

          <Divider />

          {/* 高级选项 */}
          <Card size="small" className="advanced-options">
            <Title level={5}>高级选项</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div className="option-item">
                <Text>自动切换深浅模式</Text>
                <Switch size="small" />
              </div>
              <div className="option-item">
                <Text>跟随系统设置</Text>
                <Switch size="small" />
              </div>
              <div className="option-item">
                <Text>减少动效（提升性能）</Text>
                <Switch size="small" />
              </div>
            </Space>
          </Card>

          {/* 重置选项 */}
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <Button 
              type="dashed" 
              size="small"
              onClick={() => {
                const defaultCategory = userRole === 'teacher' ? 'morandi' : 'monet';
                setUITheme(defaultCategory, 'a' as UIThemeKey, 'light');
                message.info('已重置为默认主题');
              }}
            >
              重置为默认主题
            </Button>
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default EnhancedThemeSelector;
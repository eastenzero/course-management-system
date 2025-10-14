import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Divider,
  Switch,
  Tooltip,
  Progress,
  Tag,
  Rate,
  Badge,
  Avatar,
  Timeline
} from 'antd';
import { 
  BgColorsOutlined,
  BookOutlined,
  TrophyOutlined,
  StarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  SettingOutlined,
  HeartOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';
import { 
  EnhancedGlassCard,
  EnhancedGlassButton,
  EnhancedGlassInput,
  EnhancedGlassTable,
  EnhancedGlassModal
} from '../../components/glass';
import EnhancedThemeSelector from '../../components/common/EnhancedThemeSelector';

import { glassOptimizer } from '../../utils/glassEffectOptimizer';
import './UIRedesignShowcase.css';

const { Title, Text, Paragraph } = Typography;

const UIRedesignShowcase: React.FC = () => {
  const { getThemeColors, uiTheme, toggleMode } = useTheme();
  const themeColors = getThemeColors();
  const [showModal, setShowModal] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [glassLevel, setGlassLevel] = useState<'sm' | 'md' | 'lg'>('md');

  // 获取优化器状态
  const optimizerConfig = glassOptimizer.getOptimizationConfig();
  const deviceCapabilities = glassOptimizer.getDeviceCapabilities();

  const tableColumns = [
    {
      title: '组件名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'completed' ? 'green' : 'blue'}>
          {status === 'completed' ? '已完成' : '进行中'}
        </Tag>
      )
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress 
          percent={progress} 
          size="small"
          strokeColor={themeColors?.primary}
        />
      )
    }
  ];

  const tableData = [
    {
      key: '1',
      name: 'Design Tokens系统',
      status: 'completed',
      progress: 100
    },
    {
      key: '2',
      name: '玻璃效果组件库',
      status: 'completed',
      progress: 100
    },
    {
      key: '3',
      name: '主题管理系统',
      status: 'completed',
      progress: 100
    },
    {
      key: '4',
      name: '性能优化与降级',
      status: 'completed',
      progress: 100
    }
  ];

  return (
    <div className="ui-redesign-showcase">
      {/* 标题区域 */}
      <div className="showcase-header">
        <EnhancedGlassCard 
          glassLevel="lg" 
          className="header-card"
          style={{ 
            background: `linear-gradient(135deg, ${themeColors?.primary}20, ${themeColors?.secondary}20)`
          }}
        >
          <Row align="middle" justify="space-between">
            <Col>
              <Space direction="vertical" size="small">
                <Title level={1} style={{ margin: 0, color: 'var(--neutral-text-primary)' }}>
                  UI重新设计展示 🎨
                </Title>
                <Text type="secondary" style={{ fontSize: '16px' }}>
                  基于莫奈/莫兰迪美学的现代化教育平台界面
                </Text>
                <Space>
                  <Badge 
                    count="NEW" 
                    style={{ backgroundColor: themeColors?.accent }}
                  >
                    <Text>玻璃拟态效果</Text>
                  </Badge>
                  <Text type="secondary">|</Text>
                  <Text>当前主题: <Text strong>{themeColors?.name || '默认主题'}</Text></Text>
                </Space>
              </Space>
            </Col>
            <Col>
              <Space>
                <Tooltip title="切换明暗模式">
                  <Switch 
                    checked={uiTheme.mode === 'dark'}
                    onChange={toggleMode}
                    checkedChildren="🌙"
                    unCheckedChildren="☀️"
                  />
                </Tooltip>
                <EnhancedGlassButton 
                  icon={<BgColorsOutlined />}
                  onClick={() => setShowThemeSelector(true)}
                >
                  主题设置
                </EnhancedGlassButton>
              </Space>
            </Col>
          </Row>
        </EnhancedGlassCard>
      </div>

      {/* 系统信息 */}
      <Row gutter={[24, 24]} className="system-info">
        <Col xs={24} lg={12}>
          <EnhancedGlassCard title="设备兼容性信息" glassLevel="md">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div className="info-item">
                <Text strong>backdrop-filter支持: </Text>
                <Tag color={deviceCapabilities.supportsBackdropFilter ? 'green' : 'red'}>
                  {deviceCapabilities.supportsBackdropFilter ? '支持' : '不支持'}
                </Tag>
              </div>
              <div className="info-item">
                <Text strong>设备内存: </Text>
                <Text>{deviceCapabilities.deviceMemory}GB</Text>
              </div>
              <div className="info-item">
                <Text strong>CPU核心数: </Text>
                <Text>{deviceCapabilities.hardwareConcurrency}</Text>
              </div>
              <div className="info-item">
                <Text strong>网络类型: </Text>
                <Text>{deviceCapabilities.connectionType}</Text>
              </div>
              <div className="info-item">
                <Text strong>低端设备: </Text>
                <Tag color={deviceCapabilities.isLowEndDevice ? 'orange' : 'green'}>
                  {deviceCapabilities.isLowEndDevice ? '是' : '否'}
                </Tag>
              </div>
            </Space>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} lg={12}>
          <EnhancedGlassCard title="优化配置状态" glassLevel="md">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div className="info-item">
                <Text strong>玻璃效果: </Text>
                <Tag color={optimizerConfig.enableGlass ? 'green' : 'red'}>
                  {optimizerConfig.enableGlass ? '启用' : '禁用'}
                </Tag>
              </div>
              <div className="info-item">
                <Text strong>模糊级别: </Text>
                <Text>{optimizerConfig.blurLevel}</Text>
              </div>
              <div className="info-item">
                <Text strong>最大模糊层数: </Text>
                <Text>{optimizerConfig.maxBlurLayers}</Text>
              </div>
              <div className="info-item">
                <Text strong>噪点纹理: </Text>
                <Tag color={optimizerConfig.enableNoise ? 'green' : 'red'}>
                  {optimizerConfig.enableNoise ? '启用' : '禁用'}
                </Tag>
              </div>
              <div className="info-item">
                <Text strong>动画效果: </Text>
                <Tag color={optimizerConfig.enableAnimations ? 'green' : 'red'}>
                  {optimizerConfig.enableAnimations ? '启用' : '禁用'}
                </Tag>
              </div>
            </Space>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 组件展示 */}
      <Row gutter={[24, 24]} className="component-showcase">
        <Col xs={24} lg={8}>
          <EnhancedGlassCard title="按钮组件" glassLevel={glassLevel}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <EnhancedGlassButton type="primary" block>
                主要按钮
              </EnhancedGlassButton>
              <EnhancedGlassButton block>
                默认按钮
              </EnhancedGlassButton>
              <EnhancedGlassButton type="dashed" block>
                虚线按钮
              </EnhancedGlassButton>
              <EnhancedGlassButton type="text" block>
                文本按钮
              </EnhancedGlassButton>
              <EnhancedGlassButton 
                type="primary" 
                glow 
                icon={<RocketOutlined />}
                block
              >
                发光按钮
              </EnhancedGlassButton>
            </Space>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} lg={8}>
          <EnhancedGlassCard title="输入组件" glassLevel={glassLevel}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <EnhancedGlassInput 
                placeholder="普通输入框"
                glassLevel={glassLevel}
              />
              <EnhancedGlassInput 
                placeholder="搜索..."
                prefix={<UserOutlined />}
                glassLevel={glassLevel}
              />
              <EnhancedGlassInput.Password 
                placeholder="密码输入框"
                glassLevel={glassLevel}
              />
              <EnhancedGlassInput.TextArea 
                placeholder="文本域"
                rows={3}
                glassLevel={glassLevel}
              />
            </Space>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} lg={8}>
          <EnhancedGlassCard title="统计卡片" glassLevel={glassLevel}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div className="stat-item">
                <div className="stat-icon" style={{ backgroundColor: themeColors?.primary }}>
                  <BookOutlined />
                </div>
                <div className="stat-content">
                  <Text type="secondary">总课程数</Text>
                  <Title level={3} style={{ margin: 0 }}>24</Title>
                </div>
              </div>
              
              <div className="stat-item">
                <div className="stat-icon" style={{ backgroundColor: themeColors?.secondary }}>
                  <TrophyOutlined />
                </div>
                <div className="stat-content">
                  <Text type="secondary">获得成就</Text>
                  <Title level={3} style={{ margin: 0 }}>12</Title>
                </div>
              </div>
              
              <div className="stat-item">
                <div className="stat-icon" style={{ backgroundColor: themeColors?.accent }}>
                  <StarOutlined />
                </div>
                <div className="stat-content">
                  <Text type="secondary">平均评分</Text>
                  <div>
                    <Rate disabled defaultValue={4.5} style={{ fontSize: '14px' }} />
                  </div>
                </div>
              </div>
            </Space>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 表格展示 */}
      <Row gutter={[24, 24]} className="table-showcase">
        <Col span={24}>
          <EnhancedGlassCard title="玻璃效果表格" glassLevel={glassLevel}>
            <EnhancedGlassTable
              columns={tableColumns}
              dataSource={tableData}
              glassLevel={glassLevel}
              hoverEffect
              stickyHeader
              pagination={false}
            />
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 控制面板 */}
      <Row gutter={[24, 24]} className="control-panel">
        <Col span={24}>
          <EnhancedGlassCard title="效果控制面板" glassLevel="md">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Space direction="vertical">
                  <Text strong>玻璃效果强度</Text>
                  <Space>
                    <EnhancedGlassButton 
                      size="small"
                      type={glassLevel === 'sm' ? 'primary' : 'default'}
                      onClick={() => setGlassLevel('sm')}
                    >
                      轻度
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      size="small"
                      type={glassLevel === 'md' ? 'primary' : 'default'}
                      onClick={() => setGlassLevel('md')}
                    >
                      中度
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      size="small"
                      type={glassLevel === 'lg' ? 'primary' : 'default'}
                      onClick={() => setGlassLevel('lg')}
                    >
                      重度
                    </EnhancedGlassButton>
                  </Space>
                </Space>
              </Col>
              
              <Col xs={24} sm={8}>
                <Space direction="vertical">
                  <Text strong>性能优化</Text>
                  <Space>
                    <EnhancedGlassButton 
                      size="small"
                      onClick={() => glassOptimizer.setOptimizationLevel('high')}
                    >
                      高性能
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      size="small"
                      onClick={() => glassOptimizer.setOptimizationLevel('auto')}
                    >
                      自动
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      size="small"
                      onClick={() => glassOptimizer.setOptimizationLevel('off')}
                    >
                      关闭
                    </EnhancedGlassButton>
                  </Space>
                </Space>
              </Col>
              
              <Col xs={24} sm={8}>
                <Space direction="vertical">
                  <Text strong>演示功能</Text>
                  <Space>
                    <EnhancedGlassButton 
                      size="small"
                      onClick={() => setShowModal(true)}
                    >
                      模态框
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      size="small"
                      onClick={() => setShowThemeSelector(true)}
                    >
                      主题选择
                    </EnhancedGlassButton>
                  </Space>
                </Space>
              </Col>
            </Row>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 模态框演示 */}
      <EnhancedGlassModal
        title="玻璃效果模态框"
        open={showModal}
        onCancel={() => setShowModal(false)}
        glassLevel="lg"
        backgroundBlur
        enableNoise
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Paragraph>
            这是一个具有玻璃拟态效果的模态框，展示了毛玻璃背景、高光描边和噪点纹理等特效。
          </Paragraph>
          <Timeline
            items={[
              {
                dot: <CheckCircleOutlined style={{ color: themeColors?.primary }} />,
                children: 'Design Tokens系统完成'
              },
              {
                dot: <CheckCircleOutlined style={{ color: themeColors?.secondary }} />,
                children: '玻璃效果组件库完成'
              },
              {
                dot: <CheckCircleOutlined style={{ color: themeColors?.accent }} />,
                children: '主题管理系统完成'
              },
              {
                dot: <ClockCircleOutlined style={{ color: themeColors?.tertiary }} />,
                children: '性能优化与降级完成'
              }
            ]}
          />
        </Space>
      </EnhancedGlassModal>

      {/* 主题选择器 */}
      {showThemeSelector && (
        <div className="theme-selector-overlay" onClick={() => setShowThemeSelector(false)}>
          <div className="theme-selector-panel" onClick={e => e.stopPropagation()}>
            <EnhancedThemeSelector />
            <EnhancedGlassButton 
              onClick={() => setShowThemeSelector(false)}
              style={{ marginTop: '16px' }}
              block
            >
              关闭
            </EnhancedGlassButton>
          </div>
        </div>
      )}
    </div>
  );
};

export default UIRedesignShowcase;

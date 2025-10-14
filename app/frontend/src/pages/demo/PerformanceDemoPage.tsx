import React, { useState, useMemo } from 'react';
import { Card, Typography, Space, Button, Row, Col, Switch, InputNumber } from 'antd';
import {
  VirtualTable,
  LazyImage,
  InfiniteList,
  OptimizedForm,
  PerformanceMonitor,
} from '../../components/common';

const { Title, Paragraph } = Typography;

// 生成大量测试数据
const generateLargeDataset = (count: number) => {
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `用户 ${index + 1}`,
    email: `user${index + 1}@example.com`,
    department: ['计算机学院', '数学学院', '物理学院'][index % 3],
    score: Math.floor(Math.random() * 100),
    avatar: `https://picsum.photos/40/40?random=${index}`,
  }));
};

const PerformanceDemoPage: React.FC = () => {
  const [dataCount, setDataCount] = useState(1000);
  const [useVirtual, setUseVirtual] = useState(true);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(true);

  // 生成大量数据
  const largeDataset = useMemo(() => generateLargeDataset(dataCount), [dataCount]);

  // 虚拟表格列配置
  const virtualTableColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '头像',
      dataIndex: 'avatar',
      key: 'avatar',
      width: 80,
      render: (url: string) => (
        <LazyImage
          src={url}
          style={{ width: 32, height: 32, borderRadius: '50%' }}
          placeholder="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0xNiAyMEMxOC4yMDkxIDIwIDIwIDIxLjc5MDkgMjAgMjRIMTJDMTIgMjEuNzkwOSAxMy43OTA5IDIwIDE2IDIwWiIgZmlsbD0iI0Q5RDlEOSIvPgo8Y2lyY2xlIGN4PSIxNiIgY3k9IjEyIiByPSI0IiBmaWxsPSIjRDlEOUQ5Ii8+Cjwvc3ZnPgo="
        />
      ),
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '院系',
      dataIndex: 'department',
      key: 'department',
      width: 120,
    },
    {
      title: '分数',
      dataIndex: 'score',
      key: 'score',
      width: 80,
      render: (score: number) => (
        <span style={{ color: score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#ff4d4f' }}>
          {score}
        </span>
      ),
    },
  ];

  // 无限滚动加载更多
  const loadMoreData = async (page: number) => {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const pageSize = 20;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const data = generateLargeDataset(pageSize).map((item, index) => ({
      ...item,
      id: start + index + 1,
      name: `用户 ${start + index + 1}`,
    }));

    return {
      data,
      total: 10000,
      hasMore: end < 10000,
    };
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>性能优化组件演示</Title>
      <Paragraph>
        这个页面展示了各种性能优化组件的使用效果，包括虚拟滚动表格、懒加载图片、无限滚动列表等。
      </Paragraph>

      {/* 性能监控 */}
      <PerformanceMonitor
        enabled={showPerformanceMonitor}
        showFloatingButton={true}
        onMetricsUpdate={(metrics) => {
          console.log('性能指标更新:', metrics);
        }}
      />

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 控制面板 */}
        <Card title="控制面板" size="small">
          <Row gutter={16} align="middle">
            <Col>
              <Space>
                <span>数据量:</span>
                <InputNumber
                  value={dataCount}
                  onChange={(value) => setDataCount(value || 1000)}
                  min={100}
                  max={10000}
                  step={100}
                />
              </Space>
            </Col>
            <Col>
              <Space>
                <span>虚拟滚动:</span>
                <Switch checked={useVirtual} onChange={setUseVirtual} />
              </Space>
            </Col>
            <Col>
              <Space>
                <span>性能监控:</span>
                <Switch checked={showPerformanceMonitor} onChange={setShowPerformanceMonitor} />
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 虚拟表格演示 */}
        <Card title={`虚拟表格演示 (${dataCount} 条数据)`}>
          <Paragraph>
            虚拟表格可以高效渲染大量数据，只渲染可见区域的行，大大提升性能。
          </Paragraph>
          <VirtualTable
            columns={virtualTableColumns}
            dataSource={largeDataset}
            height={400}
            virtual={useVirtual}
            virtualThreshold={100}
            rowKey="id"
            pagination={false}
            scroll={{ y: 400 }}
          />
        </Card>

        {/* 懒加载图片演示 */}
        <Card title="懒加载图片演示">
          <Paragraph>
            懒加载图片只在进入视口时才开始加载，减少初始页面加载时间。
          </Paragraph>
          <Row gutter={[16, 16]}>
            {Array.from({ length: 20 }, (_, index) => (
              <Col key={index} xs={6} sm={4} md={3} lg={2}>
                <LazyImage
                  src={`https://picsum.photos/150/150?random=${index + 100}`}
                  style={{ width: '100%', height: 'auto', borderRadius: 8 }}
                  lazy={true}
                  rootMargin="100px"
                />
              </Col>
            ))}
          </Row>
        </Card>

        {/* 无限滚动列表演示 */}
        <Card title="无限滚动列表演示">
          <Paragraph>
            无限滚动列表在用户滚动到底部时自动加载更多数据，提供流畅的浏览体验。
          </Paragraph>
          <InfiniteList
            dataSource={[]}
            loadMore={loadMoreData}
            height={300}
            pageSize={20}
            renderItem={(item: any, index) => (
              <div
                style={{
                  padding: '12px 16px',
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <LazyImage
                  src={item.avatar}
                  style={{ width: 40, height: 40, borderRadius: '50%' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{item.name}</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>{item.email}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div>{item.department}</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>分数: {item.score}</div>
                </div>
              </div>
            )}
          />
        </Card>

        {/* 优化表单演示 */}
        <Card title="优化表单演示">
          <Paragraph>
            优化表单支持防抖、数据持久化、自动保存等功能，提升用户体验。
          </Paragraph>
          <OptimizedForm
            formKey="demo-form"
            enablePersist={true}
            debounceDelay={500}
            autoSave={true}
            autoSaveInterval={10000}
            onDebouncedValuesChange={(changed, all) => {
              console.log('防抖值变化:', changed, all);
            }}
            onAutoSave={(values) => {
              console.log('自动保存:', values);
            }}
            layout="vertical"
          >
            <Row gutter={16}>
              <Col span={12}>
                <OptimizedForm.Item
                  name="name"
                  label="姓名"
                  rules={[{ required: true, message: '请输入姓名' }]}
                >
                  <input placeholder="请输入姓名" />
                </OptimizedForm.Item>
              </Col>
              <Col span={12}>
                <OptimizedForm.Item
                  name="email"
                  label="邮箱"
                  rules={[
                    { required: true, message: '请输入邮箱' },
                    { type: 'email', message: '请输入有效的邮箱地址' },
                  ]}
                >
                  <input placeholder="请输入邮箱" />
                </OptimizedForm.Item>
              </Col>
            </Row>
            <OptimizedForm.Item>
              <Button type="primary" htmlType="submit">
                提交
              </Button>
            </OptimizedForm.Item>
          </OptimizedForm>
        </Card>
      </Space>
    </div>
  );
};

export default React.memo(PerformanceDemoPage);

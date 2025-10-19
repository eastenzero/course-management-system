import React, { useState } from 'react';
import {
  Typography,
  Card,
  Tabs,
  Button,
  Space,
  Upload,
  message,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  Tooltip
} from 'antd';
import {
  UploadOutlined,
  FileOutlined,
  FolderOutlined,
  CloudUploadOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  PieChartOutlined
} from '@ant-design/icons';
import FileUpload from '../../components/files/FileUpload';
import FileManager from '../../components/files/FileManager';
import FileShare from '../../components/files/FileShare';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface FileStats {
  total_files: number;
  total_size: number;
  total_size_display: string;
  by_category: {
    [key: string]: {
      count: number;
      size: number;
      size_display: string;
    };
  };
  storage_usage: {
    used: number;
    total: number;
    percentage: number;
  };
}

const FilesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('manager');
  const [shareVisible, setShareVisible] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [fileStats, setFileStats] = useState<FileStats | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // 获取文件统计信息
  const fetchFileStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/files/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFileStats(data.data);
      }
    } catch (error) {
      console.error('获取文件统计失败:', error);
    }
  };

  React.useEffect(() => {
    fetchFileStats();
  }, [refreshKey]);

  // 上传成功回调
  const handleUploadSuccess = (files: any[]) => {
    message.success(`成功上传 ${files.length} 个文件`);
    setRefreshKey(prev => prev + 1);
    fetchFileStats();
  };

  // 上传失败回调
  const handleUploadError = (error: string) => {
    message.error(`上传失败: ${error}`);
  };

  // 分享文件
  const handleShareFile = (fileId: string) => {
    setSelectedFileId(fileId);
    setShareVisible(true);
  };

  // 获取类别颜色
  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'image': 'green',
      'video': 'blue',
      'audio': 'purple',
      'document': 'orange',
      'archive': 'red',
      'other': 'default'
    };
    return colors[category] || 'default';
  };

  // 获取类别图标
  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      'image': '🖼️',
      'video': '🎥',
      'audio': '🎵',
      'document': '📄',
      'archive': '📦',
      'other': '📁'
    };
    return icons[category] || '📄';
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <FileOutlined /> 文件管理
        </Title>
        <Text type="secondary">
          管理您的文件，支持上传、下载、分享和预览功能
        </Text>
      </div>

      {/* 文件统计卡片 */}
      {fileStats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总文件数"
                value={fileStats.total_files}
                prefix={<FileOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总大小"
                value={fileStats.total_size_display}
                prefix={<CloudUploadOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <div>
                <Text strong>存储使用率</Text>
                <Progress
                  percent={fileStats.storage_usage.percentage}
                  size="small"
                  style={{ marginTop: 8 }}
                />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {fileStats.storage_usage.used}GB / {fileStats.storage_usage.total}GB
                </Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <div>
                <Text strong>文件类型分布</Text>
                <div style={{ marginTop: 8 }}>
                  {Object.entries(fileStats.by_category).map(([category, stats]) => (
                    <div key={category} style={{ marginBottom: 4 }}>
                      <Space>
                        <span>{getCategoryIcon(category)}</span>
                        <Tag color={getCategoryColor(category)} size="small">
                          {category}
                        </Tag>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {stats.count} 个
                        </Text>
                      </Space>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* 主要内容区域 */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          tabBarExtraContent={
            <Space>
              <Tooltip title="刷新数据">
                <Button
                  icon={<PieChartOutlined />}
                  onClick={() => setRefreshKey(prev => prev + 1)}
                >
                  刷新
                </Button>
              </Tooltip>
            </Space>
          }
        >
          <TabPane
            tab={
              <span>
                <FolderOutlined />
                文件管理
              </span>
            }
            key="manager"
          >
            <FileManager
              onShare={handleShareFile}
              refreshKey={refreshKey}
              onRefresh={() => setRefreshKey(prev => prev + 1)}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <UploadOutlined />
                文件上传
              </span>
            }
            key="upload"
          >
            <FileUpload
              multiple={true}
              maxCount={10}
              maxSize={100}
              accept="*"
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
              showUploadList={true}
              listType="text"
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <ShareAltOutlined />
                分享管理
              </span>
            }
            key="shares"
          >
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Text type="secondary">
                在文件管理页面选择文件进行分享，或者在此查看已有的分享记录
              </Text>
            </div>
          </TabPane>
        </Tabs>
      </Card>

      {/* 文件分享模态框 */}
      <FileShare
        visible={shareVisible}
        fileId={selectedFileId}
        onCancel={() => {
          setShareVisible(false);
          setSelectedFileId(null);
        }}
        onSuccess={() => {
          setRefreshKey(prev => prev + 1);
        }}
      />
    </div>
  );
};

export default FilesPage;

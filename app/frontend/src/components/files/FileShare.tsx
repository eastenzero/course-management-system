import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Switch,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Typography,
  Card,
  List,
  Tag,
  message,
  Tooltip,
  QRCode,
  Tabs
} from 'antd';
import {
  ShareAltOutlined,
  CopyOutlined,
  QrcodeOutlined,
  DeleteOutlined,
  EyeOutlined,
  LinkOutlined
} from '@ant-design/icons';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import dayjs from 'dayjs';

const { Text, Title, Paragraph } = Typography;
const { TabPane } = Tabs;

interface FileInfo {
  id: string;
  original_name: string;
  file_size_display: string;
  category: string;
}

interface ShareInfo {
  id: string;
  share_token: string;
  share_url: string;
  password?: string;
  allow_download: boolean;
  allow_preview: boolean;
  expires_at?: string;
  max_downloads?: number;
  download_count: number;
  is_active: boolean;
  created_at: string;
  can_access: boolean;
  file_info: FileInfo;
}

interface FileShareProps {
  visible: boolean;
  onCancel: () => void;
  fileId?: string;
  fileInfo?: FileInfo;
}

const FileShare: React.FC<FileShareProps> = ({
  visible,
  onCancel,
  fileId,
  fileInfo
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [shareList, setShareList] = useState<ShareInfo[]>([]);
  const [currentShare, setCurrentShare] = useState<ShareInfo | null>(null);
  const [showQR, setShowQR] = useState(false);

  // 获取分享列表
  const fetchShares = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/files/shares/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setShareList(data.results || data.data || []);
      }
    } catch (error) {
      console.error('获取分享列表失败:', error);
    }
  };

  useEffect(() => {
    if (visible) {
      fetchShares();
    }
  }, [visible]);

  // 创建分享
  const handleCreateShare = async (values: any) => {
    if (!fileId) {
      message.error('请选择要分享的文件');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const shareData = {
        file: fileId,
        password: values.password || '',
        allow_download: values.allow_download ?? true,
        allow_preview: values.allow_preview ?? true,
        expires_at: values.expires_at ? values.expires_at.toISOString() : null,
        max_downloads: values.max_downloads || null
      };

      const response = await fetch('/api/files/shares/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(shareData)
      });

      if (response.ok) {
        const data = await response.json();
        message.success('分享创建成功');
        setCurrentShare(data.data);
        fetchShares();
        form.resetFields();
      } else {
        const error = await response.json();
        message.error(error.error || '分享创建失败');
      }
    } catch (error) {
      message.error('分享创建失败');
    } finally {
      setLoading(false);
    }
  };

  // 复制分享链接
  const handleCopyLink = (shareUrl: string, password?: string) => {
    let textToCopy = shareUrl;
    if (password) {
      textToCopy += `\n访问密码: ${password}`;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
      message.success('分享链接已复制到剪贴板');
    }).catch(() => {
      message.error('复制失败');
    });
  };

  // 删除分享
  const handleDeleteShare = async (shareId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/files/shares/${shareId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        message.success('分享已删除');
        fetchShares();
        if (currentShare?.id === shareId) {
          setCurrentShare(null);
        }
      } else {
        message.error('删除分享失败');
      }
    } catch (error) {
      message.error('删除分享失败');
    }
  };

  // 获取分享状态标签
  const getShareStatusTag = (share: ShareInfo) => {
    if (!share.is_active) {
      return <Tag color="red">已禁用</Tag>;
    }
    if (!share.can_access) {
      return <Tag color="orange">已失效</Tag>;
    }
    return <Tag color="green">有效</Tag>;
  };

  return (
    <Modal
      title={
        <Space>
          <ShareAltOutlined />
          文件分享
          {fileInfo && (
            <Text type="secondary">- {fileInfo.original_name}</Text>
          )}
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      width={800}
      footer={null}
    >
      <Tabs defaultActiveKey="create">
        <TabPane tab="创建分享" key="create">
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateShare}
            initialValues={{
              allow_download: true,
              allow_preview: true
            }}
          >
            <Form.Item
              label="访问密码"
              name="password"
              help="留空表示无需密码"
            >
              <Input.Password placeholder="可选，设置访问密码" />
            </Form.Item>

            <Form.Item label="权限设置">
              <Space direction="vertical">
                <Form.Item name="allow_preview" valuePropName="checked" noStyle>
                  <Switch checkedChildren="允许预览" unCheckedChildren="禁止预览" />
                </Form.Item>
                <Form.Item name="allow_download" valuePropName="checked" noStyle>
                  <Switch checkedChildren="允许下载" unCheckedChildren="禁止下载" />
                </Form.Item>
              </Space>
            </Form.Item>

            <Form.Item
              label="过期时间"
              name="expires_at"
              help="留空表示永不过期"
            >
              <DatePicker
                showTime
                placeholder="选择过期时间"
                style={{ width: '100%' }}
                disabledDate={(current) => current && current < dayjs().endOf('day')}
              />
            </Form.Item>

            <Form.Item
              label="最大下载次数"
              name="max_downloads"
              help="留空表示不限制下载次数"
            >
              <InputNumber
                min={1}
                placeholder="最大下载次数"
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                创建分享链接
              </Button>
            </Form.Item>
          </Form>

          {currentShare && (
            <Card title="分享链接已创建" style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>分享链接:</Text>
                  <Paragraph copyable={{ text: currentShare.share_url }}>
                    <a href={currentShare.share_url} target="_blank" rel="noopener noreferrer">
                      {currentShare.share_url}
                    </a>
                  </Paragraph>
                </div>

                {currentShare.password && (
                  <div>
                    <Text strong>访问密码:</Text>
                    <Paragraph copyable={{ text: currentShare.password }}>
                      {currentShare.password}
                    </Paragraph>
                  </div>
                )}

                <Space>
                  <Button
                    icon={<CopyOutlined />}
                    onClick={() => handleCopyLink(currentShare.share_url, currentShare.password)}
                  >
                    复制链接
                  </Button>
                  <Button
                    icon={<QrcodeOutlined />}
                    onClick={() => setShowQR(true)}
                  >
                    生成二维码
                  </Button>
                </Space>
              </Space>
            </Card>
          )}
        </TabPane>

        <TabPane tab="分享管理" key="manage">
          <List
            dataSource={shareList}
            renderItem={(share) => (
              <List.Item
                actions={[
                  <Tooltip title="查看">
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={() => window.open(share.share_url, '_blank')}
                    />
                  </Tooltip>,
                  <Tooltip title="复制链接">
                    <Button
                      type="text"
                      icon={<CopyOutlined />}
                      onClick={() => handleCopyLink(share.share_url, share.password)}
                    />
                  </Tooltip>,
                  <Tooltip title="删除">
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDeleteShare(share.id)}
                    />
                  </Tooltip>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{share.file_info.original_name}</Text>
                      {getShareStatusTag(share)}
                      {share.password && (
                        <Tag color="blue" icon={<LinkOutlined />}>
                          有密码
                        </Tag>
                      )}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={4}>
                      <Text type="secondary">
                        创建时间: {formatDistanceToNow(new Date(share.created_at), {
                          addSuffix: true,
                          locale: zhCN
                        })}
                      </Text>
                      {share.expires_at && (
                        <Text type="secondary">
                          过期时间: {new Date(share.expires_at).toLocaleString()}
                        </Text>
                      )}
                      <Text type="secondary">
                        下载次数: {share.download_count}
                        {share.max_downloads && ` / ${share.max_downloads}`}
                      </Text>
                      <Space>
                        {share.allow_preview && <Tag size="small">可预览</Tag>}
                        {share.allow_download && <Tag size="small">可下载</Tag>}
                      </Space>
                    </Space>
                  }
                />
              </List.Item>
            )}
            locale={{ emptyText: '暂无分享记录' }}
          />
        </TabPane>
      </Tabs>

      {/* 二维码模态框 */}
      <Modal
        title="分享二维码"
        open={showQR}
        onCancel={() => setShowQR(false)}
        footer={[
          <Button key="close" onClick={() => setShowQR(false)}>
            关闭
          </Button>
        ]}
      >
        {currentShare && (
          <div style={{ textAlign: 'center' }}>
            <QRCode value={currentShare.share_url} size={200} />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">扫描二维码访问分享文件</Text>
              {currentShare.password && (
                <div style={{ marginTop: 8 }}>
                  <Text strong>访问密码: {currentShare.password}</Text>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>
    </Modal>
  );
};

export default FileShare;

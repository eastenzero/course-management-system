import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Input,
  Select,
  Tag,
  Modal,
  message,
  Tooltip,
  Card,
  Row,
  Col,
  Statistic,
  Dropdown,
  Checkbox
} from 'antd';
import type { ColumnsType, TableRowSelection } from 'antd/es/table';
import {
  SearchOutlined,
  DownloadOutlined,
  DeleteOutlined,
  ShareAltOutlined,
  EyeOutlined,
  ReloadOutlined,
  MoreOutlined,
  FileOutlined,
  FolderOutlined
} from '@ant-design/icons';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const { Search } = Input;
const { Option } = Select;

interface FileInfo {
  id: string;
  original_name: string;
  file_url: string;
  file_size: number;
  file_size_display: string;
  mime_type: string;
  category: string;
  status: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  download_count: number;
  uploaded_by_name: string;
  can_delete: boolean;
  can_share: boolean;
}

interface FileManagerProps {
  showUpload?: boolean;
  allowSelection?: boolean;
  onFileSelect?: (files: FileInfo[]) => void;
  onShare?: (fileId: string) => void;
  refreshKey?: number;
  onRefresh?: () => void;
  className?: string;
}

const FileManager: React.FC<FileManagerProps> = ({
  showUpload = true,
  allowSelection = false,
  onFileSelect,
  onShare,
  refreshKey,
  onRefresh,
  className = ''
}) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  });

  // 获取文件列表
  const fetchFiles = async (params: any = {}) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const queryParams = new URLSearchParams({
        page: params.current || pagination.current,
        page_size: params.pageSize || pagination.pageSize,
        ...params.filters
      });

      if (searchText) {
        queryParams.append('search', searchText);
      }
      if (categoryFilter) {
        queryParams.append('category', categoryFilter);
      }
      if (statusFilter) {
        queryParams.append('status', statusFilter);
      }

      const response = await fetch(`/api/files/?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data.results || data.data || []);
        setPagination(prev => ({
          ...prev,
          total: data.count || data.total || 0,
          current: params.current || prev.current
        }));
      } else {
        message.error('获取文件列表失败');
      }
    } catch (error) {
      message.error('获取文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [searchText, categoryFilter, statusFilter, refreshKey]);

  // 获取文件类型图标
  const getFileIcon = (category: string) => {
    const iconMap: { [key: string]: string } = {
      'image': '🖼️',
      'video': '🎥',
      'audio': '🎵',
      'document': '📄',
      'archive': '📦',
      'other': '📁'
    };
    return iconMap[category] || '📁';
  };

  // 获取分类标签颜色
  const getCategoryColor = (category: string) => {
    const colorMap: { [key: string]: string } = {
      'image': 'green',
      'video': 'blue',
      'audio': 'purple',
      'document': 'orange',
      'archive': 'red',
      'other': 'default'
    };
    return colorMap[category] || 'default';
  };

  // 下载文件
  const handleDownload = async (file: FileInfo) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/files/${file.id}/download/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.original_name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        message.success('文件下载成功');
      } else {
        message.error('文件下载失败');
      }
    } catch (error) {
      message.error('文件下载失败');
    }
  };

  // 删除文件
  const handleDelete = (file: FileInfo) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${file.original_name}" 吗？`,
      onOk: async () => {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch(`/api/files/${file.id}/`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            message.success('文件删除成功');
            fetchFiles();
          } else {
            message.error('文件删除失败');
          }
        } catch (error) {
          message.error('文件删除失败');
        }
      }
    });
  };

  // 批量操作
  const handleBulkOperation = (action: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    const actionText = {
      'delete': '删除',
      'make_public': '设为公开',
      'make_private': '设为私有'
    }[action] || action;

    Modal.confirm({
      title: `确认${actionText}`,
      content: `确定要${actionText}选中的 ${selectedRowKeys.length} 个文件吗？`,
      onOk: async () => {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch('/api/files/bulk-operation/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              file_ids: selectedRowKeys,
              action
            })
          });

          if (response.ok) {
            const data = await response.json();
            message.success(data.message);
            setSelectedRowKeys([]);
            fetchFiles();
          } else {
            message.error(`${actionText}失败`);
          }
        } catch (error) {
          message.error(`${actionText}失败`);
        }
      }
    });
  };

  // 表格列定义
  const columns: ColumnsType<FileInfo> = [
    {
      title: '文件名',
      dataIndex: 'original_name',
      key: 'original_name',
      render: (text, record) => (
        <Space>
          <span style={{ fontSize: 16 }}>
            {getFileIcon(record.category)}
          </span>
          <span>{text}</span>
          {record.is_public && (
            <Tag color="blue" size="small">公开</Tag>
          )}
        </Space>
      ),
      sorter: true
    },
    {
      title: '类型',
      dataIndex: 'category',
      key: 'category',
      render: (category) => (
        <Tag color={getCategoryColor(category)}>
          {category}
        </Tag>
      ),
      filters: [
        { text: '图片', value: 'image' },
        { text: '视频', value: 'video' },
        { text: '音频', value: 'audio' },
        { text: '文档', value: 'document' },
        { text: '压缩包', value: 'archive' },
        { text: '其他', value: 'other' }
      ]
    },
    {
      title: '大小',
      dataIndex: 'file_size_display',
      key: 'file_size',
      sorter: true
    },
    {
      title: '下载次数',
      dataIndex: 'download_count',
      key: 'download_count',
      sorter: true
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => (
        <Tooltip title={new Date(date).toLocaleString()}>
          {formatDistanceToNow(new Date(date), { addSuffix: true, locale: zhCN })}
        </Tooltip>
      ),
      sorter: true
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => window.open(record.file_url, '_blank')}
            />
          </Tooltip>
          <Tooltip title="下载">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(record)}
            />
          </Tooltip>
          {record.can_share && (
            <Tooltip title="分享">
              <Button
                type="text"
                icon={<ShareAltOutlined />}
                onClick={() => onShare?.(record.id)}
              />
            </Tooltip>
          )}
          {record.can_delete && (
            <Tooltip title="删除">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(record)}
              />
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  // 行选择配置
  const rowSelection: TableRowSelection<FileInfo> = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys, selectedRows) => {
      setSelectedRowKeys(newSelectedRowKeys);
      if (allowSelection && onFileSelect) {
        onFileSelect(selectedRows);
      }
    }
  };

  return (
    <div className={className}>
      <Card>
        {/* 工具栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col flex="auto">
            <Space>
              <Search
                placeholder="搜索文件名"
                allowClear
                style={{ width: 200 }}
                onSearch={setSearchText}
              />
              <Select
                placeholder="文件类型"
                allowClear
                style={{ width: 120 }}
                value={categoryFilter || undefined}
                onChange={setCategoryFilter}
              >
                <Option value="image">图片</Option>
                <Option value="video">视频</Option>
                <Option value="audio">音频</Option>
                <Option value="document">文档</Option>
                <Option value="archive">压缩包</Option>
                <Option value="other">其他</Option>
              </Select>
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 100 }}
                value={statusFilter || undefined}
                onChange={setStatusFilter}
              >
                <Option value="active">正常</Option>
                <Option value="deleted">已删除</Option>
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              {selectedRowKeys.length > 0 && (
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'delete',
                        label: '删除选中',
                        icon: <DeleteOutlined />,
                        onClick: () => handleBulkOperation('delete')
                      },
                      {
                        key: 'make_public',
                        label: '设为公开',
                        onClick: () => handleBulkOperation('make_public')
                      },
                      {
                        key: 'make_private',
                        label: '设为私有',
                        onClick: () => handleBulkOperation('make_private')
                      }
                    ]
                  }}
                >
                  <Button icon={<MoreOutlined />}>
                    批量操作 ({selectedRowKeys.length})
                  </Button>
                </Dropdown>
              )}
              <Button
                icon={<ReloadOutlined />}
                onClick={() => fetchFiles()}
                loading={loading}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 文件表格 */}
        <Table
          columns={columns}
          dataSource={files}
          rowKey="id"
          loading={loading}
          rowSelection={allowSelection ? rowSelection : undefined}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
          }}
          onChange={(paginationConfig, filters, sorter) => {
            fetchFiles({
              current: paginationConfig.current,
              pageSize: paginationConfig.pageSize,
              filters,
              sorter
            });
          }}
        />
      </Card>
    </div>
  );
};

export default FileManager;

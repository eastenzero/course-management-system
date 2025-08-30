import React, { useState } from 'react';
import {
  Upload,
  Button,
  Progress,
  message,
  Space,
  Typography,
  Card,
  List,
  Tag,
  Tooltip,
  Modal
} from 'antd';
import {
  UploadOutlined,
  InboxOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface FileUploadProps {
  multiple?: boolean;
  maxCount?: number;
  maxSize?: number; // MB
  accept?: string;
  onUploadSuccess?: (files: any[]) => void;
  onUploadError?: (error: string) => void;
  showUploadList?: boolean;
  listType?: 'text' | 'picture' | 'picture-card';
  className?: string;
}

interface UploadedFileInfo {
  id: string;
  original_name: string;
  file_url: string;
  file_size: number;
  file_size_display: string;
  mime_type: string;
  category: string;
  created_at: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  multiple = true,
  maxCount = 10,
  maxSize = 100,
  accept = '*',
  onUploadSuccess,
  onUploadError,
  showUploadList = true,
  listType = 'text',
  className = ''
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileInfo[]>([]);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState<UploadedFileInfo | null>(null);

  // 获取文件类型图标
  const getFileIcon = (mimeType: string, category: string) => {
    if (category === 'image') {
      return '🖼️';
    } else if (category === 'video') {
      return '🎥';
    } else if (category === 'audio') {
      return '🎵';
    } else if (category === 'document') {
      return '📄';
    } else if (category === 'archive') {
      return '📦';
    }
    return '📁';
  };

  // 获取文件类型标签颜色
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

  // 文件上传前的验证
  const beforeUpload = (file: File) => {
    // 文件大小验证
    const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
    if (!isLtMaxSize) {
      message.error(`文件大小不能超过 ${maxSize}MB`);
      return false;
    }

    // 文件类型验证
    if (accept !== '*') {
      const acceptedTypes = accept.split(',').map(type => type.trim());
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const isAccepted = acceptedTypes.some(type => 
        type === fileExtension || 
        type === file.type ||
        (type.endsWith('/*') && file.type.startsWith(type.replace('/*', '')))
      );
      
      if (!isAccepted) {
        message.error(`不支持的文件类型: ${fileExtension}`);
        return false;
      }
    }

    return true;
  };

  // 自定义上传请求
  const customRequest = async (options: any) => {
    const { file, onSuccess, onError, onProgress } = options;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('original_name', file.name);

    try {
      const token = localStorage.getItem('access_token');
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress({ percent });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200 || xhr.status === 201) {
          const response = JSON.parse(xhr.responseText);
          onSuccess(response.data);
          
          // 添加到已上传文件列表
          setUploadedFiles(prev => [response.data, ...prev]);
          
          message.success(`${file.name} 上传成功`);
        } else {
          const error = JSON.parse(xhr.responseText);
          onError(new Error(error.error || '上传失败'));
          message.error(`${file.name} 上传失败`);
        }
      });

      xhr.addEventListener('error', () => {
        onError(new Error('网络错误'));
        message.error(`${file.name} 上传失败`);
      });

      xhr.open('POST', '/api/files/');
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);

    } catch (error) {
      onError(error);
      message.error(`${file.name} 上传失败`);
    }
  };

  // 文件列表变化处理
  const handleChange: UploadProps['onChange'] = (info) => {
    let newFileList = [...info.fileList];

    // 限制文件数量
    newFileList = newFileList.slice(-maxCount);

    // 更新文件状态
    newFileList = newFileList.map(file => {
      if (file.response) {
        file.url = file.response.file_url;
      }
      return file;
    });

    setFileList(newFileList);

    // 检查是否所有文件都上传完成
    const allDone = newFileList.every(file => 
      file.status === 'done' || file.status === 'error'
    );
    
    if (allDone) {
      setUploading(false);
      const successFiles = newFileList
        .filter(file => file.status === 'done')
        .map(file => file.response);
      
      if (successFiles.length > 0) {
        onUploadSuccess?.(successFiles);
      }
    }
  };

  // 开始上传
  const handleUpload = () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }
    setUploading(true);
  };

  // 预览文件
  const handlePreview = (file: UploadedFileInfo) => {
    setPreviewFile(file);
    setPreviewVisible(true);
  };

  // 删除文件
  const handleDelete = (fileId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个文件吗？',
      onOk: async () => {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch(`/api/files/${fileId}/`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
            message.success('文件删除成功');
          } else {
            message.error('文件删除失败');
          }
        } catch (error) {
          message.error('文件删除失败');
        }
      }
    });
  };

  const uploadProps: UploadProps = {
    multiple,
    fileList,
    beforeUpload,
    customRequest,
    onChange: handleChange,
    showUploadList: showUploadList,
    listType,
  };

  return (
    <div className={className}>
      <Card title="文件上传" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Dragger {...uploadProps} style={{ padding: '20px' }}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text">
              点击或拖拽文件到此区域上传
            </p>
            <p className="ant-upload-hint">
              支持单个或批量上传，最大文件大小 {maxSize}MB
              {accept !== '*' && (
                <Text type="secondary">
                  <br />支持格式: {accept}
                </Text>
              )}
            </p>
          </Dragger>

          {fileList.length > 0 && !showUploadList && (
            <Button
              type="primary"
              onClick={handleUpload}
              loading={uploading}
              icon={<UploadOutlined />}
            >
              {uploading ? '上传中...' : '开始上传'}
            </Button>
          )}
        </Space>
      </Card>

      {uploadedFiles.length > 0 && (
        <Card title="已上传文件" size="small" style={{ marginTop: 16 }}>
          <List
            dataSource={uploadedFiles}
            renderItem={(file) => (
              <List.Item
                actions={[
                  <Tooltip title="预览">
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={() => handlePreview(file)}
                    />
                  </Tooltip>,
                  <Tooltip title="删除">
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(file.id)}
                    />
                  </Tooltip>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <span style={{ fontSize: 24 }}>
                      {getFileIcon(file.mime_type, file.category)}
                    </span>
                  }
                  title={
                    <Space>
                      <Text strong>{file.original_name}</Text>
                      <Tag color={getCategoryColor(file.category)}>
                        {file.category}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space>
                      <Text type="secondary">{file.file_size_display}</Text>
                      <Text type="secondary">
                        {new Date(file.created_at).toLocaleString()}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* 文件预览模态框 */}
      <Modal
        title="文件预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="download" type="primary">
            <a href={previewFile?.file_url} download target="_blank" rel="noopener noreferrer">
              下载文件
            </a>
          </Button>,
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {previewFile && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>文件名: </Text>
                <Text>{previewFile.original_name}</Text>
              </div>
              <div>
                <Text strong>文件大小: </Text>
                <Text>{previewFile.file_size_display}</Text>
              </div>
              <div>
                <Text strong>文件类型: </Text>
                <Text>{previewFile.mime_type}</Text>
              </div>
              <div>
                <Text strong>上传时间: </Text>
                <Text>{new Date(previewFile.created_at).toLocaleString()}</Text>
              </div>
              
              {previewFile.category === 'image' && (
                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <img
                    src={previewFile.file_url}
                    alt={previewFile.original_name}
                    style={{ maxWidth: '100%', maxHeight: 400 }}
                  />
                </div>
              )}
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default FileUpload;

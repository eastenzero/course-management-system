import React, { useState } from 'react';
import {
  Modal,
  Button,
  Upload,
  message,
  Steps,
  Table,
  Alert,
  Space,
  Typography,
  Progress,
  Divider,
  Card,
  Select,
  Form,
  Input,
  Checkbox
} from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  FileExcelOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import * as XLSX from 'xlsx';

const { Step } = Steps;
const { Text, Title } = Typography;
const { Option } = Select;

interface ScheduleImportExportProps {
  visible: boolean;
  onCancel: () => void;
  onImportSuccess?: (data: any[]) => void;
  onExportRequest?: (options: ExportOptions) => void;
  mode: 'import' | 'export';
  semester?: string;
}

interface ExportOptions {
  semester: string;
  format: 'excel' | 'csv';
  includeWeekend: boolean;
  includeEmptySlots: boolean;
  groupBy: 'teacher' | 'classroom' | 'course';
}

interface ImportData {
  course_code: string;
  course_name: string;
  teacher_name: string;
  classroom: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  week_range: string;
  [key: string]: any;
}

const ScheduleImportExport: React.FC<ScheduleImportExportProps> = ({
  visible,
  onCancel,
  onImportSuccess,
  onExportRequest,
  mode,
  semester = ''
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [importData, setImportData] = useState<ImportData[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [importProgress, setImportProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [form] = Form.useForm();

  // 导入步骤
  const importSteps = [
    { title: '上传文件', description: '选择Excel或CSV文件' },
    { title: '数据预览', description: '检查导入数据' },
    { title: '验证数据', description: '验证数据格式和内容' },
    { title: '导入完成', description: '完成数据导入' }
  ];

  // 导出步骤
  const exportSteps = [
    { title: '选择选项', description: '配置导出参数' },
    { title: '生成文件', description: '生成导出文件' },
    { title: '下载文件', description: '下载生成的文件' }
  ];

  const steps = mode === 'import' ? importSteps : exportSteps;

  // 文件上传配置
  const uploadProps: UploadProps = {
    accept: '.xlsx,.xls,.csv',
    fileList,
    beforeUpload: (file) => {
      const isValidType = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                         file.type === 'application/vnd.ms-excel' ||
                         file.type === 'text/csv';
      
      if (!isValidType) {
        message.error('只支持Excel和CSV文件格式！');
        return false;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过10MB！');
        return false;
      }

      setFileList([file]);
      parseFile(file);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setFileList([]);
      setImportData([]);
      setCurrentStep(0);
    }
  };

  // 解析文件
  const parseFile = async (file: File) => {
    setIsProcessing(true);
    
    try {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: 'buffer' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

      // 假设第一行是标题行
      const headers = jsonData[0] as string[];
      const rows = jsonData.slice(1) as any[][];

      const parsedData: ImportData[] = rows.map((row, index) => {
        const item: any = {};
        headers.forEach((header, headerIndex) => {
          item[header] = row[headerIndex] || '';
        });
        return item;
      }).filter(item => item.course_code || item.course_name); // 过滤空行

      setImportData(parsedData);
      setCurrentStep(1);
      message.success('文件解析成功！');
    } catch (error) {
      message.error('文件解析失败，请检查文件格式！');
      console.error('File parsing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // 验证导入数据
  const validateData = () => {
    const errors: string[] = [];
    const requiredFields = ['course_code', 'course_name', 'teacher_name', 'day_of_week', 'start_time', 'end_time'];

    importData.forEach((item, index) => {
      requiredFields.forEach(field => {
        if (!item[field]) {
          errors.push(`第${index + 2}行缺少必需字段: ${field}`);
        }
      });

      // 验证星期
      const dayOfWeek = parseInt(item.day_of_week);
      if (isNaN(dayOfWeek) || dayOfWeek < 1 || dayOfWeek > 7) {
        errors.push(`第${index + 2}行星期值无效: ${item.day_of_week}`);
      }

      // 验证时间格式
      const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
      if (!timeRegex.test(item.start_time)) {
        errors.push(`第${index + 2}行开始时间格式错误: ${item.start_time}`);
      }
      if (!timeRegex.test(item.end_time)) {
        errors.push(`第${index + 2}行结束时间格式错误: ${item.end_time}`);
      }
    });

    setValidationErrors(errors);
    setCurrentStep(2);

    if (errors.length === 0) {
      message.success('数据验证通过！');
    } else {
      message.warning(`发现${errors.length}个验证错误，请检查数据！`);
    }
  };

  // 执行导入
  const executeImport = async () => {
    if (validationErrors.length > 0) {
      message.error('请先修复数据验证错误！');
      return;
    }

    setIsProcessing(true);
    setImportProgress(0);

    try {
      // 模拟导入进度
      for (let i = 0; i <= 100; i += 10) {
        setImportProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      onImportSuccess?.(importData);
      setCurrentStep(3);
      message.success('数据导入成功！');
    } catch (error) {
      message.error('数据导入失败！');
      console.error('Import error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // 执行导出
  const executeExport = async () => {
    const values = await form.validateFields();
    setIsProcessing(true);

    try {
      onExportRequest?.(values);
      setCurrentStep(2);
      message.success('导出文件生成成功！');
    } catch (error) {
      message.error('导出失败！');
      console.error('Export error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // 重置状态
  const resetState = () => {
    setCurrentStep(0);
    setFileList([]);
    setImportData([]);
    setValidationErrors([]);
    setImportProgress(0);
    setIsProcessing(false);
    form.resetFields();
  };

  // 关闭弹窗
  const handleCancel = () => {
    resetState();
    onCancel();
  };

  // 表格列配置
  const columns = [
    { title: '课程代码', dataIndex: 'course_code', key: 'course_code', width: 100 },
    { title: '课程名称', dataIndex: 'course_name', key: 'course_name', width: 150 },
    { title: '教师', dataIndex: 'teacher_name', key: 'teacher_name', width: 100 },
    { title: '教室', dataIndex: 'classroom', key: 'classroom', width: 100 },
    { title: '星期', dataIndex: 'day_of_week', key: 'day_of_week', width: 80 },
    { title: '开始时间', dataIndex: 'start_time', key: 'start_time', width: 100 },
    { title: '结束时间', dataIndex: 'end_time', key: 'end_time', width: 100 },
    { title: '周次', dataIndex: 'week_range', key: 'week_range', width: 120 },
  ];

  const renderImportContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Upload.Dragger {...uploadProps} style={{ marginBottom: '20px' }}>
              <p className="ant-upload-drag-icon">
                <FileExcelOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持Excel (.xlsx, .xls) 和 CSV 文件格式，文件大小不超过10MB
              </p>
            </Upload.Dragger>
            
            <Alert
              message="导入格式说明"
              description={
                <div>
                  <p>Excel文件应包含以下列：</p>
                  <ul style={{ textAlign: 'left', marginTop: '8px' }}>
                    <li>course_code: 课程代码</li>
                    <li>course_name: 课程名称</li>
                    <li>teacher_name: 教师姓名</li>
                    <li>classroom: 教室</li>
                    <li>day_of_week: 星期 (1-7)</li>
                    <li>start_time: 开始时间 (HH:MM)</li>
                    <li>end_time: 结束时间 (HH:MM)</li>
                    <li>week_range: 周次范围 (如: 1-16周)</li>
                  </ul>
                </div>
              }
              type="info"
              showIcon
            />
          </div>
        );

      case 1:
        return (
          <div>
            <Alert
              message={`共解析到 ${importData.length} 条课程安排数据`}
              type="success"
              showIcon
              style={{ marginBottom: '16px' }}
            />
            
            <Table
              columns={columns}
              dataSource={importData}
              rowKey={(record, index) => index?.toString() || '0'}
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800, y: 400 }}
              size="small"
            />
            
            <div style={{ marginTop: '16px', textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setCurrentStep(0)}>上一步</Button>
                <Button type="primary" onClick={validateData}>
                  验证数据
                </Button>
              </Space>
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            {validationErrors.length === 0 ? (
              <Alert
                message="数据验证通过"
                description="所有数据格式正确，可以开始导入"
                type="success"
                showIcon
                style={{ marginBottom: '16px' }}
              />
            ) : (
              <Alert
                message={`发现 ${validationErrors.length} 个验证错误`}
                description={
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    {validationErrors.map((error, index) => (
                      <div key={index} style={{ marginBottom: '4px' }}>
                        <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: '4px' }} />
                        {error}
                      </div>
                    ))}
                  </div>
                }
                type="error"
                showIcon
                style={{ marginBottom: '16px' }}
              />
            )}
            
            {isProcessing && (
              <div style={{ marginBottom: '16px' }}>
                <Text>导入进度:</Text>
                <Progress percent={importProgress} status="active" />
              </div>
            )}
            
            <div style={{ textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setCurrentStep(1)} disabled={isProcessing}>
                  上一步
                </Button>
                <Button 
                  type="primary" 
                  onClick={executeImport}
                  disabled={validationErrors.length > 0 || isProcessing}
                  loading={isProcessing}
                >
                  开始导入
                </Button>
              </Space>
            </div>
          </div>
        );

      case 3:
        return (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={3}>导入完成</Title>
            <Text type="secondary">
              成功导入 {importData.length} 条课程安排数据
            </Text>
          </div>
        );

      default:
        return null;
    }
  };

  const renderExportContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Form form={form} layout="vertical" initialValues={{ 
            semester, 
            format: 'excel', 
            includeWeekend: false, 
            includeEmptySlots: false,
            groupBy: 'teacher'
          }}>
            <Form.Item
              name="semester"
              label="学期"
              rules={[{ required: true, message: '请选择学期' }]}
            >
              <Input placeholder="如: 2024-2025-1" />
            </Form.Item>
            
            <Form.Item
              name="format"
              label="导出格式"
              rules={[{ required: true, message: '请选择导出格式' }]}
            >
              <Select>
                <Option value="excel">Excel (.xlsx)</Option>
                <Option value="csv">CSV (.csv)</Option>
              </Select>
            </Form.Item>
            
            <Form.Item
              name="groupBy"
              label="分组方式"
              rules={[{ required: true, message: '请选择分组方式' }]}
            >
              <Select>
                <Option value="teacher">按教师分组</Option>
                <Option value="classroom">按教室分组</Option>
                <Option value="course">按课程分组</Option>
              </Select>
            </Form.Item>
            
            <Form.Item name="includeWeekend" valuePropName="checked">
              <Checkbox>包含周末</Checkbox>
            </Form.Item>
            
            <Form.Item name="includeEmptySlots" valuePropName="checked">
              <Checkbox>包含空时间段</Checkbox>
            </Form.Item>
            
            <div style={{ textAlign: 'right' }}>
              <Button type="primary" onClick={executeExport} loading={isProcessing}>
                生成导出文件
              </Button>
            </div>
          </Form>
        );

      case 1:
        return (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Progress type="circle" percent={100} status="success" />
            <Title level={4} style={{ marginTop: '16px' }}>文件生成成功</Title>
            <Text type="secondary">导出文件已准备就绪</Text>
          </div>
        );

      case 2:
        return (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={3}>导出完成</Title>
            <Text type="secondary">文件已成功下载到本地</Text>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {mode === 'import' ? <UploadOutlined style={{ marginRight: '8px' }} /> : <DownloadOutlined style={{ marginRight: '8px' }} />}
          {mode === 'import' ? '导入课程表' : '导出课程表'}
        </div>
      }
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Steps current={currentStep} style={{ marginBottom: '24px' }}>
        {steps.map((step, index) => (
          <Step key={index} title={step.title} description={step.description} />
        ))}
      </Steps>
      
      <Divider />
      
      {mode === 'import' ? renderImportContent() : renderExportContent()}
    </Modal>
  );
};

export default ScheduleImportExport;

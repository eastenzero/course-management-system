import React, { useState } from 'react';
import { 
  Table, 
  Tag, 
  Input, 
  Button, 
  Space, 
  Typography, 
  Tooltip,
  Modal,
  Form,
  InputNumber,
  Select,
  message
} from 'antd';
import {
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  TrophyOutlined,
  UserOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Text } = Typography;
const { Option } = Select;

export interface GradeRecord {
  id: number;
  student_id: string;
  student_name: string;
  course_id?: number;
  course_name?: string;
  score?: number;
  grade?: string;
  status?: string;
  enrollment_id?: number;
  [key: string]: any;
}

export interface GradeTableProps {
  data: GradeRecord[];
  loading?: boolean;
  editable?: boolean;
  mode?: 'student' | 'teacher';
  showCourse?: boolean;
  showStudent?: boolean;
  onGradeUpdate?: (record: GradeRecord, newScore: number) => Promise<void>;
  onBatchUpdate?: (updates: Array<{ id: number; score: number }>) => Promise<void>;
  columns?: ColumnsType<GradeRecord>;
  pagination?: any;
  className?: string;
  style?: React.CSSProperties;
}

const GradeTable: React.FC<GradeTableProps> = ({
  data,
  loading = false,
  editable = false,
  mode = 'student',
  showCourse = true,
  showStudent = true,
  onGradeUpdate,
  onBatchUpdate,
  columns: customColumns,
  pagination,
  className,
  style
}) => {
  const [editingKey, setEditingKey] = useState<number | null>(null);
  const [editingScore, setEditingScore] = useState<number | undefined>();
  const [batchEditVisible, setBatchEditVisible] = useState(false);
  const [batchForm] = Form.useForm();

  const getGradeColor = (score?: number) => {
    if (score === undefined || score === null) return '#666';
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 70) return '#faad14';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  const getGradeLetter = (score?: number) => {
    if (score === undefined || score === null) return '';
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getStatusColor = (status?: string) => {
    const colorMap: Record<string, string> = {
      'enrolled': 'blue',
      'completed': 'green',
      'dropped': 'red',
      'failed': 'red'
    };
    return colorMap[status || ''] || 'default';
  };

  const handleEdit = (record: GradeRecord) => {
    setEditingKey(record.id);
    setEditingScore(record.score);
  };

  const handleSave = async (record: GradeRecord) => {
    if (editingScore === undefined || editingScore < 0 || editingScore > 100) {
      message.error('请输入有效的成绩（0-100）');
      return;
    }

    try {
      await onGradeUpdate?.(record, editingScore);
      setEditingKey(null);
      setEditingScore(undefined);
      message.success('成绩更新成功');
    } catch (error) {
      message.error('成绩更新失败');
    }
  };

  const handleCancel = () => {
    setEditingKey(null);
    setEditingScore(undefined);
  };

  const handleBatchUpdate = async (values: any) => {
    try {
      const updates = data
        .filter(record => values[`score_${record.id}`] !== undefined)
        .map(record => ({
          id: record.enrollment_id || record.id,
          score: values[`score_${record.id}`]
        }));

      await onBatchUpdate?.(updates);
      setBatchEditVisible(false);
      batchForm.resetFields();
      message.success('批量更新成功');
    } catch (error) {
      message.error('批量更新失败');
    }
  };

  const defaultColumns: ColumnsType<GradeRecord> = [
    ...(showStudent ? [{
      title: '学生信息',
      key: 'student',
      render: (_, record: GradeRecord) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              {record.student_name}
            </div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              学号：{record.student_id}
            </div>
          </div>
        </div>
      ),
    }] : []),
    
    ...(showCourse ? [{
      title: '课程信息',
      key: 'course',
      render: (_, record: GradeRecord) => (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {record.course_name}
          </div>
          {record.course_id && (
            <div style={{ color: '#666', fontSize: '12px' }}>
              课程ID：{record.course_id}
            </div>
          )}
        </div>
      ),
    }] : []),

    {
      title: '成绩',
      key: 'score',
      render: (_, record: GradeRecord) => {
        const isEditing = editingKey === record.id;
        
        if (isEditing && editable) {
          return (
            <Space>
              <InputNumber
                min={0}
                max={100}
                precision={1}
                value={editingScore}
                onChange={setEditingScore}
                style={{ width: '80px' }}
              />
              <Button
                type="link"
                icon={<SaveOutlined />}
                onClick={() => handleSave(record)}
                size="small"
              />
              <Button
                type="link"
                icon={<CloseOutlined />}
                onClick={handleCancel}
                size="small"
              />
            </Space>
          );
        }

        return (
          <div style={{ textAlign: 'center' }}>
            {record.score !== undefined && record.score !== null ? (
              <>
                <div style={{ 
                  fontSize: '16px', 
                  fontWeight: 'bold', 
                  color: getGradeColor(record.score),
                  marginBottom: '4px'
                }}>
                  {record.score}
                </div>
                <Tag color={getGradeColor(record.score)}>
                  {record.grade || getGradeLetter(record.score)}
                </Tag>
              </>
            ) : (
              <Text type="secondary">未录入</Text>
            )}
          </div>
        );
      },
      sorter: (a, b) => (a.score || 0) - (b.score || 0),
    },

    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        if (!status) return null;
        const statusMap: Record<string, string> = {
          'enrolled': '进行中',
          'completed': '已完成',
          'dropped': '已退课',
          'failed': '未通过'
        };
        return (
          <Tag color={getStatusColor(status)}>
            {statusMap[status] || status}
          </Tag>
        );
      },
    },

    ...(editable && mode === 'teacher' ? [{
      title: '操作',
      key: 'actions',
      render: (_, record: GradeRecord) => {
        const isEditing = editingKey === record.id;
        
        if (isEditing) {
          return null; // 编辑状态下操作按钮已在成绩列显示
        }

        return (
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
        );
      },
    }] : []),
  ];

  const finalColumns = customColumns || defaultColumns;

  return (
    <div className={className} style={style}>
      {editable && mode === 'teacher' && onBatchUpdate && (
        <div style={{ marginBottom: '16px', textAlign: 'right' }}>
          <Button
            type="primary"
            onClick={() => setBatchEditVisible(true)}
          >
            批量录入成绩
          </Button>
        </div>
      )}

      <Table
        columns={finalColumns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        scroll={{ x: 'max-content' }}
      />

      {/* 批量录入模态框 */}
      <Modal
        title="批量录入成绩"
        open={batchEditVisible}
        onCancel={() => setBatchEditVisible(false)}
        onOk={() => batchForm.submit()}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={batchForm}
          onFinish={handleBatchUpdate}
          layout="vertical"
        >
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {data.map(record => (
              <div key={record.id} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                marginBottom: '12px',
                padding: '8px',
                backgroundColor: '#fafafa',
                borderRadius: '4px'
              }}>
                <div style={{ flex: 1 }}>
                  <Text strong>{record.student_name}</Text>
                  <Text type="secondary" style={{ marginLeft: '8px' }}>
                    ({record.student_id})
                  </Text>
                </div>
                <Form.Item
                  name={`score_${record.id}`}
                  style={{ margin: 0, width: '100px' }}
                  initialValue={record.score}
                >
                  <InputNumber
                    min={0}
                    max={100}
                    precision={1}
                    placeholder="成绩"
                  />
                </Form.Item>
              </div>
            ))}
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default GradeTable;

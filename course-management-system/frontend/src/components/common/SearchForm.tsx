import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Row, Col, Space, DatePicker, InputNumber } from 'antd';
import { SearchOutlined, ReloadOutlined, DownOutlined, UpOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

export interface SearchField {
  /** 字段名 */
  name: string;
  /** 字段标签 */
  label: string;
  /** 字段类型 */
  type: 'input' | 'select' | 'date' | 'dateRange' | 'number';
  /** 占位符 */
  placeholder?: string;
  /** 选项（用于select类型） */
  options?: Array<{ label: string; value: any }>;
  /** 默认值 */
  defaultValue?: any;
  /** 是否必填 */
  required?: boolean;
  /** 列宽度 */
  span?: number;
  /** 自定义渲染 */
  render?: (field: SearchField) => React.ReactNode;
  /** 额外的组件属性 */
  props?: any;
}

export interface SearchFormProps {
  /** 搜索字段配置 */
  fields: SearchField[];
  /** 搜索回调 */
  onSearch: (values: any) => void;
  /** 重置回调 */
  onReset?: () => void;
  /** 初始值 */
  initialValues?: any;
  /** 是否显示重置按钮 */
  showReset?: boolean;
  /** 是否显示展开/收起 */
  showExpand?: boolean;
  /** 默认展开行数 */
  defaultExpandRows?: number;
  /** 是否加载中 */
  loading?: boolean;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
}

const SearchForm: React.FC<SearchFormProps> = ({
  fields,
  onSearch,
  onReset,
  initialValues,
  showReset = true,
  showExpand = true,
  defaultExpandRows = 1,
  loading = false,
  style,
  className,
}) => {
  const [form] = Form.useForm();
  const [expanded, setExpanded] = useState(false);

  // 计算需要展开的字段
  const fieldsPerRow = 3; // 每行显示3个字段
  const expandThreshold = defaultExpandRows * fieldsPerRow;
  const shouldShowExpand = showExpand && fields.length > expandThreshold;
  const visibleFields = shouldShowExpand && !expanded 
    ? fields.slice(0, expandThreshold) 
    : fields;

  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue(initialValues);
    }
  }, [initialValues, form]);

  const handleSearch = () => {
    const values = form.getFieldsValue();
    // 过滤空值
    const filteredValues = Object.keys(values).reduce((acc, key) => {
      const value = values[key];
      if (value !== undefined && value !== null && value !== '') {
        // 处理日期范围
        if (Array.isArray(value) && value.length === 2) {
          acc[key] = value.map(date => dayjs(date).format('YYYY-MM-DD'));
        } else if (dayjs.isDayjs(value)) {
          acc[key] = value.format('YYYY-MM-DD');
        } else {
          acc[key] = value;
        }
      }
      return acc;
    }, {} as any);
    
    onSearch(filteredValues);
  };

  const handleReset = () => {
    form.resetFields();
    if (onReset) {
      onReset();
    } else {
      onSearch({});
    }
  };

  const renderField = (field: SearchField) => {
    if (field.render) {
      return field.render(field);
    }

    const commonProps = {
      placeholder: field.placeholder || `请输入${field.label}`,
    };

    switch (field.type) {
      case 'select':
        return (
          <Select {...commonProps} allowClear>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        );
      case 'date':
        return <DatePicker {...commonProps} style={{ width: '100%' }} />;
      case 'dateRange':
        return <RangePicker
          placeholder={[`请选择开始${field.label}`, `请选择结束${field.label}`]}
          {...field.props}
          style={{ width: '100%' }}
        />;
      case 'number':
        return <InputNumber {...commonProps} style={{ width: '100%' }} />;
      default:
        return <Input {...commonProps} />;
    }
  };

  return (
    <div className={className} style={style}>
      <Form
        form={form}
        layout="vertical"
        initialValues={initialValues}
        onFinish={handleSearch}
      >
        <Row gutter={[16, 16]}>
          {visibleFields.map((field) => (
            <Col
              key={field.name}
              xs={24}
              sm={12}
              md={field.span || 8}
              lg={field.span || 6}
            >
              <Form.Item
                name={field.name}
                label={field.label}
                rules={field.required ? [{ required: true, message: `请输入${field.label}` }] : []}
              >
                {renderField(field)}
              </Form.Item>
            </Col>
          ))}
          
          {/* 操作按钮 */}
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label=" " style={{ marginBottom: 0 }}>
              <Space>
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                >
                  搜索
                </Button>
                {showReset && (
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={handleReset}
                  >
                    重置
                  </Button>
                )}
                {shouldShowExpand && (
                  <Button
                    type="link"
                    icon={expanded ? <UpOutlined /> : <DownOutlined />}
                    onClick={() => setExpanded(!expanded)}
                  >
                    {expanded ? '收起' : '展开'}
                  </Button>
                )}
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </div>
  );
};

export default SearchForm;

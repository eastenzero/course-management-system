import React from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Switch,
  Radio,
  Checkbox,
  Upload,
  Button,
  Row,
  Col,
} from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { FormInstance, Rule } from 'antd/es/form';

const { Option } = Select;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

export interface FormFieldOption {
  label: string;
  value: any;
  disabled?: boolean;
}

export interface FormFieldConfig {
  /** 字段名 */
  name: string;
  /** 字段标签 */
  label: string;
  /** 字段类型 */
  type: 'input' | 'textarea' | 'select' | 'date' | 'dateRange' | 'number' | 'switch' | 'radio' | 'checkbox' | 'upload' | 'password';
  /** 占位符 */
  placeholder?: string;
  /** 选项（用于select、radio、checkbox类型） */
  options?: FormFieldOption[];
  /** 验证规则 */
  rules?: Rule[];
  /** 默认值 */
  defaultValue?: any;
  /** 是否禁用 */
  disabled?: boolean;
  /** 是否隐藏 */
  hidden?: boolean;
  /** 列宽度 */
  span?: number;
  /** 额外属性 */
  props?: Record<string, any>;
  /** 依赖字段（当依赖字段值变化时重新渲染） */
  dependencies?: string[];
  /** 条件显示（返回true时显示） */
  condition?: (values: any) => boolean;
  /** 自定义渲染 */
  render?: (field: FormFieldConfig, form: FormInstance) => React.ReactNode;
  /** 帮助文本 */
  help?: string;
  /** 额外信息 */
  extra?: React.ReactNode;
}

export interface FormBuilderProps {
  /** 表单字段配置 */
  fields: FormFieldConfig[];
  /** 表单实例 */
  form?: FormInstance;
  /** 初始值 */
  initialValues?: Record<string, any>;
  /** 表单布局 */
  layout?: 'horizontal' | 'vertical' | 'inline';
  /** 标签列宽度（horizontal布局时） */
  labelCol?: any;
  /** 包装列宽度（horizontal布局时） */
  wrapperCol?: any;
  /** 提交回调 */
  onFinish?: (values: any) => void;
  /** 提交失败回调 */
  onFinishFailed?: (errorInfo: any) => void;
  /** 值变化回调 */
  onValuesChange?: (changedValues: any, allValues: any) => void;
  /** 是否显示提交按钮 */
  showSubmit?: boolean;
  /** 提交按钮文本 */
  submitText?: string;
  /** 是否显示重置按钮 */
  showReset?: boolean;
  /** 重置按钮文本 */
  resetText?: string;
  /** 是否加载中 */
  loading?: boolean;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
}

const FormBuilder: React.FC<FormBuilderProps> = ({
  fields,
  form: externalForm,
  initialValues,
  layout = 'vertical',
  labelCol,
  wrapperCol,
  onFinish,
  onFinishFailed,
  onValuesChange,
  showSubmit = true,
  submitText = '提交',
  showReset = false,
  resetText = '重置',
  loading = false,
  style,
  className,
}) => {
  const [internalForm] = Form.useForm();
  const form = externalForm || internalForm;

  const renderField = (field: FormFieldConfig) => {
    if (field.render) {
      return field.render(field, form);
    }

    const commonProps = {
      placeholder: field.placeholder || `请输入${field.label}`,
      disabled: field.disabled,
      ...field.props,
    };

    switch (field.type) {
      case 'textarea':
        return <TextArea {...commonProps} rows={4} />;
      
      case 'select':
        return (
          <Select {...commonProps} allowClear>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value} disabled={option.disabled}>
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
          disabled={field.disabled}
          {...field.props}
          style={{ width: '100%' }}
        />;
      
      case 'number':
        return <InputNumber {...commonProps} style={{ width: '100%' }} />;
      
      case 'switch':
        return <Switch {...commonProps} />;
      
      case 'radio':
        return (
          <Radio.Group {...commonProps}>
            {field.options?.map(option => (
              <Radio key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </Radio>
            ))}
          </Radio.Group>
        );
      
      case 'checkbox':
        return (
          <Checkbox.Group {...commonProps}>
            {field.options?.map(option => (
              <Checkbox key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </Checkbox>
            ))}
          </Checkbox.Group>
        );
      
      case 'upload':
        return (
          <Upload {...commonProps}>
            <Button icon={<UploadOutlined />}>点击上传</Button>
          </Upload>
        );
      
      case 'password':
        return <Input.Password {...commonProps} />;
      
      default:
        return <Input {...commonProps} />;
    }
  };

  const getVisibleFields = () => {
    const formValues = form.getFieldsValue();
    return fields.filter(field => {
      if (field.hidden) return false;
      if (field.condition) {
        return field.condition(formValues);
      }
      return true;
    });
  };

  return (
    <Form
      form={form}
      layout={layout}
      labelCol={labelCol}
      wrapperCol={wrapperCol}
      initialValues={initialValues}
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      onValuesChange={onValuesChange}
      style={style}
      className={className}
    >
      <Row gutter={[16, 16]}>
        {getVisibleFields().map((field) => (
          <Col
            key={field.name}
            xs={24}
            sm={field.span || 24}
            md={field.span || 12}
            lg={field.span || 8}
          >
            <Form.Item
              name={field.name}
              label={field.label}
              rules={field.rules}
              dependencies={field.dependencies}
              help={field.help}
              extra={field.extra}
            >
              {renderField(field)}
            </Form.Item>
          </Col>
        ))}
        
        {(showSubmit || showReset) && (
          <Col xs={24}>
            <Form.Item>
              <div style={{ textAlign: 'right' }}>
                {showReset && (
                  <Button
                    style={{ marginRight: 8 }}
                    onClick={() => form.resetFields()}
                  >
                    {resetText}
                  </Button>
                )}
                {showSubmit && (
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                  >
                    {submitText}
                  </Button>
                )}
              </div>
            </Form.Item>
          </Col>
        )}
      </Row>
    </Form>
  );
};

export default FormBuilder;

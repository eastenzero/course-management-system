import React, { useState, useEffect } from 'react';
import { Card, Checkbox, Radio, Select, Slider, Button, Space, Divider, Collapse, Tag } from 'antd';
import { FilterOutlined, ClearOutlined } from '@ant-design/icons';

const { Option } = Select;
const { Panel } = Collapse;
const CheckboxGroup = Checkbox.Group;
const { Group: RadioGroup } = Radio;

export interface FilterOption {
  label: string;
  value: any;
  count?: number;
}

export interface FilterConfig {
  /** 过滤器名称 */
  name: string;
  /** 过滤器标题 */
  title: string;
  /** 过滤器类型 */
  type: 'checkbox' | 'radio' | 'select' | 'range' | 'tags';
  /** 选项列表 */
  options?: FilterOption[];
  /** 默认值 */
  defaultValue?: any;
  /** 是否多选（用于select） */
  multiple?: boolean;
  /** 范围配置（用于range类型） */
  range?: {
    min: number;
    max: number;
    step?: number;
    marks?: Record<number, string>;
  };
  /** 是否默认展开 */
  defaultExpanded?: boolean;
  /** 自定义渲染 */
  render?: (config: FilterConfig, value: any, onChange: (value: any) => void) => React.ReactNode;
}

export interface FilterPanelProps {
  /** 过滤器配置 */
  filters: FilterConfig[];
  /** 过滤变化回调 */
  onChange: (filters: Record<string, any>) => void;
  /** 初始过滤值 */
  initialValues?: Record<string, any>;
  /** 是否显示清除按钮 */
  showClear?: boolean;
  /** 是否显示应用按钮 */
  showApply?: boolean;
  /** 是否实时更新 */
  realtime?: boolean;
  /** 标题 */
  title?: string;
  /** 是否可折叠 */
  collapsible?: boolean;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onChange,
  initialValues = {},
  showClear = true,
  showApply = false,
  realtime = true,
  title = '筛选条件',
  collapsible = false,
  style,
  className,
}) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [activeKeys, setActiveKeys] = useState<string[]>(
    filters.filter(f => f.defaultExpanded !== false).map(f => f.name)
  );

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const handleValueChange = (name: string, value: any) => {
    const newValues = { ...values, [name]: value };
    setValues(newValues);
    
    if (realtime) {
      onChange(newValues);
    }
  };

  const handleClear = () => {
    setValues({});
    onChange({});
  };

  const handleApply = () => {
    onChange(values);
  };

  const renderFilter = (filter: FilterConfig) => {
    const value = values[filter.name];

    if (filter.render) {
      return filter.render(filter, value, (newValue) => handleValueChange(filter.name, newValue));
    }

    switch (filter.type) {
      case 'checkbox':
        return (
          <CheckboxGroup
            options={filter.options?.map(opt => ({
              label: `${opt.label}${opt.count ? ` (${opt.count})` : ''}`,
              value: opt.value,
            }))}
            value={value || []}
            onChange={(checkedValues: any) => handleValueChange(filter.name, checkedValues)}
          />
        );

      case 'radio':
        return (
          <RadioGroup
            value={value}
            onChange={(e) => handleValueChange(filter.name, e.target.value)}
          >
            <Space direction="vertical">
              {filter.options?.map(opt => (
                <Radio key={opt.value} value={opt.value}>
                  {opt.label}{opt.count ? ` (${opt.count})` : ''}
                </Radio>
              ))}
            </Space>
          </RadioGroup>
        );

      case 'select':
        return (
          <Select
            style={{ width: '100%' }}
            placeholder={`请选择${filter.title}`}
            value={value}
            onChange={(selectValue) => handleValueChange(filter.name, selectValue)}
            mode={filter.multiple ? 'multiple' : undefined}
            allowClear
          >
            {filter.options?.map(opt => (
              <Option key={opt.value} value={opt.value}>
                {opt.label}{opt.count ? ` (${opt.count})` : ''}
              </Option>
            ))}
          </Select>
        );

      case 'range':
        if (!filter.range) return null;
        return (
          <div style={{ padding: '0 8px' }}>
            <Slider
              range
              min={filter.range.min}
              max={filter.range.max}
              step={filter.range.step || 1}
              marks={filter.range.marks}
              value={value || [filter.range.min, filter.range.max]}
              onChange={(rangeValue) => handleValueChange(filter.name, rangeValue)}
            />
          </div>
        );

      case 'tags':
        return (
          <div>
            {filter.options?.map(opt => (
              <Tag.CheckableTag
                key={opt.value}
                checked={(value || []).includes(opt.value)}
                onChange={(checked) => {
                  const currentValues = value || [];
                  const newValues = checked
                    ? [...currentValues, opt.value]
                    : currentValues.filter((v: any) => v !== opt.value);
                  handleValueChange(filter.name, newValues);
                }}
              >
                {opt.label}{opt.count ? ` (${opt.count})` : ''}
              </Tag.CheckableTag>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  const hasActiveFilters = Object.keys(values).some(key => {
    const value = values[key];
    return value !== undefined && value !== null && 
           (Array.isArray(value) ? value.length > 0 : value !== '');
  });

  const content = (
    <div>
      {collapsible ? (
        <Collapse
          activeKey={activeKeys}
          onChange={setActiveKeys}
          ghost
        >
          {filters.map(filter => (
            <Panel key={filter.name} header={filter.title}>
              {renderFilter(filter)}
            </Panel>
          ))}
        </Collapse>
      ) : (
        filters.map((filter, index) => (
          <div key={filter.name}>
            <div style={{ fontWeight: 500, marginBottom: 12 }}>
              {filter.title}
            </div>
            <div style={{ marginBottom: 16 }}>
              {renderFilter(filter)}
            </div>
            {index < filters.length - 1 && <Divider />}
          </div>
        ))
      )}

      {(showClear || showApply) && (
        <>
          <Divider />
          <Space>
            {showClear && (
              <Button
                icon={<ClearOutlined />}
                onClick={handleClear}
                disabled={!hasActiveFilters}
              >
                清除
              </Button>
            )}
            {showApply && (
              <Button
                type="primary"
                icon={<FilterOutlined />}
                onClick={handleApply}
              >
                应用
              </Button>
            )}
          </Space>
        </>
      )}
    </div>
  );

  return (
    <Card
      title={title}
      size="small"
      style={style}
      className={className}
      bodyStyle={{ padding: 16 }}
    >
      {content}
    </Card>
  );
};

export default FilterPanel;

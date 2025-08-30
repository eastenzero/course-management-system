import React, { useCallback, useEffect, useMemo, useRef, memo } from 'react';
import { Form, FormProps, FormInstance } from 'antd';
import { useDebouncedCallback, usePersistedForm } from '../../hooks';

export interface OptimizedFormProps extends Omit<FormProps, 'autoSave'> {
  /** 表单唯一标识，用于数据持久化 */
  formKey?: string;
  /** 是否启用数据持久化 */
  enablePersist?: boolean;
  /** 防抖延迟时间（毫秒） */
  debounceDelay?: number;
  /** 值变化回调（防抖） */
  onDebouncedValuesChange?: (changedValues: any, allValues: any) => void;
  /** 是否启用自动保存 */
  autoSave?: boolean;
  /** 自动保存间隔（毫秒） */
  autoSaveInterval?: number;
  /** 自动保存回调 */
  onAutoSave?: (values: any) => void;
  /** 表单验证模式 */
  validateMode?: 'onChange' | 'onBlur' | 'onSubmit';
  /** 是否启用实时验证 */
  realTimeValidation?: boolean;
  /** 是否启用字段级别的优化 */
  optimizeFields?: boolean;
  /** 表单提交前的数据处理 */
  beforeSubmit?: (values: any) => any;
  /** 表单提交后的回调 */
  afterSubmit?: (values: any, result: any) => void;
  /** 错误处理回调 */
  onError?: (error: any) => void;
  /** 自定义验证规则 */
  customValidators?: Record<string, (value: any, values: any) => Promise<void> | void>;
  /** 是否启用性能监控 */
  enablePerformanceMonitoring?: boolean;
  /** 子组件 */
  children?: React.ReactNode;
}

const OptimizedForm: React.FC<OptimizedFormProps> = memo(({
  formKey,
  enablePersist = false,
  debounceDelay = 300,
  onDebouncedValuesChange,
  autoSave = false,
  autoSaveInterval = 30000, // 30秒
  onAutoSave,
  validateMode = 'onChange',
  realTimeValidation = false,
  optimizeFields = true,
  beforeSubmit,
  afterSubmit,
  onError,
  customValidators = {},
  enablePerformanceMonitoring = false,
  onValuesChange,
  onFinish,
  initialValues,
  children,
  ...props
}) => {
  const [form] = Form.useForm(props.form);
  const validationTimersRef = useRef<Map<string, NodeJS.Timeout>>(new Map());
  const lastValidationRef = useRef<Map<string, any>>(new Map());
  const performanceRef = useRef({
    renderCount: 0,
    validationCount: 0,
    submitCount: 0,
    startTime: Date.now(),
  });

  // 性能监控
  useEffect(() => {
    if (enablePerformanceMonitoring) {
      performanceRef.current.renderCount += 1;
      console.log('[Form Performance]', {
        formKey,
        renderCount: performanceRef.current.renderCount,
        totalTime: Date.now() - performanceRef.current.startTime,
      });
    }
  });

  // 数据持久化
  const {
    formData,
    updateMultipleFields,
    resetForm,
    clearFormData,
  } = usePersistedForm(
    formKey || 'default-form',
    initialValues || {}
  );

  // 防抖的值变化处理
  const debouncedValuesChange = useDebouncedCallback(
    (changedValues: any, allValues: any) => {
      if (onDebouncedValuesChange) {
        onDebouncedValuesChange(changedValues, allValues);
      }

      // 持久化数据
      if (enablePersist) {
        updateMultipleFields(allValues);
      }
    },
    debounceDelay
  );

  // 自动保存
  const debouncedAutoSave = useDebouncedCallback(
    (values: any) => {
      if (onAutoSave) {
        onAutoSave(values);
      }
    },
    autoSaveInterval
  );

  // 处理值变化
  const handleValuesChange = useCallback(
    (changedValues: any, allValues: any) => {
      // 立即回调
      if (onValuesChange) {
        onValuesChange(changedValues, allValues);
      }

      // 防抖回调
      debouncedValuesChange(changedValues, allValues);

      // 自动保存
      if (autoSave) {
        debouncedAutoSave(allValues);
      }
    },
    [onValuesChange, debouncedValuesChange, autoSave, debouncedAutoSave]
  );

  // 初始化表单数据
  useEffect(() => {
    if (enablePersist && formKey && Object.keys(formData).length > 0) {
      form.setFieldsValue(formData);
    } else if (initialValues) {
      form.setFieldsValue(initialValues);
    }
  }, [form, enablePersist, formKey, formData, initialValues]);

  // 实时验证
  const validateTrigger = useMemo(() => {
    if (!realTimeValidation) return undefined;
    
    switch (validateMode) {
      case 'onChange':
        return 'onChange';
      case 'onBlur':
        return 'onBlur';
      default:
        return undefined;
    }
  }, [realTimeValidation, validateMode]);

  // 优化的表单配置
  const optimizedProps = useMemo(() => ({
    ...props,
    form,
    onValuesChange: handleValuesChange,
    validateTrigger,
    preserve: false, // 不保留已卸载字段的值
    scrollToFirstError: true, // 验证失败时滚动到第一个错误字段
  }), [props, form, handleValuesChange, validateTrigger]);

  // 优化的表单提交处理
  const handleFinish = useCallback(async (values: any) => {
    try {
      if (enablePerformanceMonitoring) {
        performanceRef.current.submitCount += 1;
      }

      // 数据预处理
      const processedValues = beforeSubmit ? beforeSubmit(values) : values;

      // 执行提交
      const result = await onFinish?.(processedValues);

      // 提交后处理
      if (afterSubmit) {
        afterSubmit(processedValues, result);
      }

      // 清除持久化数据
      if (enablePersist) {
        clearFormData();
      }

      return result;
    } catch (error) {
      if (onError) {
        onError(error);
      } else {
        console.error('Form submission error:', error);
      }
      throw error;
    }
  }, [onFinish, beforeSubmit, afterSubmit, onError, enablePersist, clearFormData, enablePerformanceMonitoring]);

  // 自定义验证处理
  const handleCustomValidation = useCallback(async (changedFields: any[], allValues: any) => {
    for (const field of changedFields) {
      const { name, value } = field;
      const fieldName = Array.isArray(name) ? name.join('.') : name;

      // 检查值是否真的改变了
      if (lastValidationRef.current.get(fieldName) === value) {
        continue;
      }

      lastValidationRef.current.set(fieldName, value);

      // 执行自定义验证
      if (customValidators[fieldName]) {
        try {
          await customValidators[fieldName](value, allValues);
          if (enablePerformanceMonitoring) {
            performanceRef.current.validationCount += 1;
          }
        } catch (error) {
          form.setFields([{
            name,
            errors: [error instanceof Error ? error.message : String(error)]
          }]);
        }
      }
    }
  }, [customValidators, form, enablePerformanceMonitoring]);

  // 清理持久化数据的方法
  const clearPersistedData = useCallback(() => {
    if (enablePersist) {
      clearFormData();
    }
  }, [enablePersist, clearFormData]);

  // 重置表单的方法
  const resetFormData = useCallback(() => {
    form.resetFields();
    if (enablePersist) {
      resetForm();
    }
  }, [form, enablePersist, resetForm]);

  // 暴露额外的方法
  useEffect(() => {
    if (form && typeof form === 'object') {
      (form as any).clearPersistedData = clearPersistedData;
      (form as any).resetFormData = resetFormData;
      (form as any).getPerformanceStats = () => performanceRef.current;
    }
  }, [form, clearPersistedData, resetFormData]);

  // 清理定时器
  useEffect(() => {
    return () => {
      validationTimersRef.current.forEach(timer => clearTimeout(timer));
      validationTimersRef.current.clear();
    };
  }, []);

  return (
    <Form
      {...optimizedProps}
      onFinish={handleFinish}
    >
      {children}
    </Form>
  );
});

// 高阶组件：为表单项添加优化
export const withFormItemOptimization = <P extends object>(
  Component: React.ComponentType<P>
) => {
  const OptimizedComponent = React.memo((props: P) => {
    return <Component {...props} />;
  });

  OptimizedComponent.displayName = `withFormItemOptimization(${Component.displayName || Component.name})`;
  
  return OptimizedComponent;
};

// 优化的表单项组件
export const OptimizedFormItem = React.memo(Form.Item);

// 导出优化的表单和相关组件
export default OptimizedForm;

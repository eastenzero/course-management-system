import { useState, useEffect, useCallback } from 'react';

/**
 * 本地存储Hook
 * @param key 存储键名
 * @param initialValue 初始值
 * @returns [值, 设置值函数, 删除函数]
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // 获取初始值
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // 设置值
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // 删除值
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

/**
 * 会话存储Hook
 * @param key 存储键名
 * @param initialValue 初始值
 * @returns [值, 设置值函数, 删除函数]
 */
export function useSessionStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // 获取初始值
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // 设置值
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // 删除值
  const removeValue = useCallback(() => {
    try {
      window.sessionStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

/**
 * 存储状态Hook（支持localStorage和sessionStorage）
 * @param key 存储键名
 * @param initialValue 初始值
 * @param storage 存储类型
 * @returns 存储相关的状态和方法
 */
export function useStorageState<T>(
  key: string,
  initialValue: T,
  storage: 'localStorage' | 'sessionStorage' = 'localStorage'
) {
  const storageObject = storage === 'localStorage' ? window.localStorage : window.sessionStorage;

  const [value, setValue] = useState<T>(() => {
    try {
      const item = storageObject.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading ${storage} key "${key}":`, error);
      return initialValue;
    }
  });

  const setStoredValue = useCallback((newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      storageObject.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting ${storage} key "${key}":`, error);
    }
  }, [key, value, storageObject, storage]);

  const removeStoredValue = useCallback(() => {
    try {
      storageObject.removeItem(key);
      setValue(initialValue);
    } catch (error) {
      console.error(`Error removing ${storage} key "${key}":`, error);
    }
  }, [key, initialValue, storageObject, storage]);

  return {
    value,
    setValue: setStoredValue,
    removeValue: removeStoredValue,
  };
}

/**
 * 用户偏好设置Hook
 * @param key 设置键名
 * @param defaultValue 默认值
 * @returns 偏好设置相关的状态和方法
 */
export function useUserPreference<T>(key: string, defaultValue: T) {
  const storageKey = `user_preference_${key}`;
  const [preference, setPreference, removePreference] = useLocalStorage(storageKey, defaultValue);

  const updatePreference = useCallback((updates: Partial<T>) => {
    setPreference(prev => ({ ...prev, ...updates }));
  }, [setPreference]);

  const resetPreference = useCallback(() => {
    setPreference(defaultValue);
  }, [setPreference, defaultValue]);

  return {
    preference,
    setPreference,
    updatePreference,
    resetPreference,
    removePreference,
  };
}

/**
 * 表单数据持久化Hook
 * @param formKey 表单键名
 * @param initialValues 初始值
 * @returns 表单数据相关的状态和方法
 */
export function usePersistedForm<T extends Record<string, any>>(
  formKey: string,
  initialValues: T
) {
  const storageKey = `form_data_${formKey}`;
  const [formData, setFormData, clearFormData] = useLocalStorage(storageKey, initialValues);

  const updateFormData = useCallback((field: keyof T, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, [setFormData]);

  const updateMultipleFields = useCallback((updates: Partial<T>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  }, [setFormData]);

  const resetForm = useCallback(() => {
    setFormData(initialValues);
  }, [setFormData, initialValues]);

  return {
    formData,
    setFormData,
    updateFormData,
    updateMultipleFields,
    resetForm,
    clearFormData,
  };
}

export default useLocalStorage;

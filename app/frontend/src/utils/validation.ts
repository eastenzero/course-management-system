/**
 * 验证工具函数
 */

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否有效
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证手机号格式
 * @param phone 手机号
 * @returns 是否有效
 */
export function validatePhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 验证身份证号格式
 * @param idCard 身份证号
 * @returns 是否有效
 */
export function validateIdCard(idCard: string): boolean {
  const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
  return idCardRegex.test(idCard);
}

/**
 * 验证密码强度
 * @param password 密码
 * @param options 验证选项
 * @returns 验证结果
 */
export function validatePassword(
  password: string,
  options: {
    minLength?: number;
    maxLength?: number;
    requireUppercase?: boolean;
    requireLowercase?: boolean;
    requireNumbers?: boolean;
    requireSpecialChars?: boolean;
  } = {}
): { isValid: boolean; errors: string[] } {
  const {
    minLength = 6,
    maxLength = 20,
    requireUppercase = false,
    requireLowercase = false,
    requireNumbers = false,
    requireSpecialChars = false,
  } = options;

  const errors: string[] = [];

  if (password.length < minLength) {
    errors.push(`密码长度不能少于${minLength}位`);
  }

  if (password.length > maxLength) {
    errors.push(`密码长度不能超过${maxLength}位`);
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('密码必须包含大写字母');
  }

  if (requireLowercase && !/[a-z]/.test(password)) {
    errors.push('密码必须包含小写字母');
  }

  if (requireNumbers && !/\d/.test(password)) {
    errors.push('密码必须包含数字');
  }

  if (requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('密码必须包含特殊字符');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * 验证URL格式
 * @param url URL地址
 * @returns 是否有效
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 验证IP地址格式
 * @param ip IP地址
 * @returns 是否有效
 */
export function validateIP(ip: string): boolean {
  const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipRegex.test(ip);
}

/**
 * 验证数字范围
 * @param value 数值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在范围内
 */
export function validateNumberRange(
  value: number,
  min?: number,
  max?: number
): boolean {
  if (min !== undefined && value < min) return false;
  if (max !== undefined && value > max) return false;
  return true;
}

/**
 * 验证字符串长度
 * @param str 字符串
 * @param min 最小长度
 * @param max 最大长度
 * @returns 是否在范围内
 */
export function validateStringLength(
  str: string,
  min?: number,
  max?: number
): boolean {
  if (min !== undefined && str.length < min) return false;
  if (max !== undefined && str.length > max) return false;
  return true;
}

/**
 * 验证日期格式
 * @param date 日期字符串
 * @param format 日期格式
 * @returns 是否有效
 */
export function validateDate(date: string, format?: string): boolean {
  if (!date) return false;
  
  const dateObj = new Date(date);
  return !isNaN(dateObj.getTime());
}

/**
 * 验证文件类型
 * @param file 文件对象
 * @param allowedTypes 允许的文件类型
 * @returns 是否允许
 */
export function validateFileType(
  file: File,
  allowedTypes: string[]
): boolean {
  return allowedTypes.includes(file.type);
}

/**
 * 验证文件大小
 * @param file 文件对象
 * @param maxSize 最大大小（字节）
 * @returns 是否符合要求
 */
export function validateFileSize(file: File, maxSize: number): boolean {
  return file.size <= maxSize;
}

/**
 * 验证中文姓名
 * @param name 姓名
 * @returns 是否有效
 */
export function validateChineseName(name: string): boolean {
  const chineseNameRegex = /^[\u4e00-\u9fa5]{2,10}$/;
  return chineseNameRegex.test(name);
}

/**
 * 验证学号格式
 * @param studentId 学号
 * @returns 是否有效
 */
export function validateStudentId(studentId: string): boolean {
  // 假设学号为8-12位数字
  const studentIdRegex = /^\d{8,12}$/;
  return studentIdRegex.test(studentId);
}

/**
 * 验证工号格式
 * @param employeeId 工号
 * @returns 是否有效
 */
export function validateEmployeeId(employeeId: string): boolean {
  // 假设工号为6-10位数字或字母数字组合
  const employeeIdRegex = /^[A-Za-z0-9]{6,10}$/;
  return employeeIdRegex.test(employeeId);
}

/**
 * 验证课程代码格式
 * @param courseCode 课程代码
 * @returns 是否有效
 */
export function validateCourseCode(courseCode: string): boolean {
  // 假设课程代码为字母+数字组合，如CS101, MATH201
  const courseCodeRegex = /^[A-Z]{2,4}\d{3,4}$/;
  return courseCodeRegex.test(courseCode);
}

/**
 * 验证教室编号格式
 * @param roomNumber 教室编号
 * @returns 是否有效
 */
export function validateRoomNumber(roomNumber: string): boolean {
  // 假设教室编号格式为：楼号+房间号，如A101, B205
  const roomNumberRegex = /^[A-Z]\d{3,4}$/;
  return roomNumberRegex.test(roomNumber);
}

/**
 * 通用验证器
 * @param value 值
 * @param rules 验证规则
 * @returns 验证结果
 */
export function validate(
  value: any,
  rules: Array<{
    validator: (value: any) => boolean;
    message: string;
  }>
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  for (const rule of rules) {
    if (!rule.validator(value)) {
      errors.push(rule.message);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * 创建必填验证器
 * @param message 错误消息
 * @returns 验证器
 */
export function required(message: string = '此字段为必填项') {
  return {
    validator: (value: any) => {
      if (typeof value === 'string') {
        return value.trim().length > 0;
      }
      return value !== null && value !== undefined;
    },
    message,
  };
}

/**
 * 创建最小长度验证器
 * @param min 最小长度
 * @param message 错误消息
 * @returns 验证器
 */
export function minLength(min: number, message?: string) {
  return {
    validator: (value: string) => value.length >= min,
    message: message || `长度不能少于${min}位`,
  };
}

/**
 * 创建最大长度验证器
 * @param max 最大长度
 * @param message 错误消息
 * @returns 验证器
 */
export function maxLength(max: number, message?: string) {
  return {
    validator: (value: string) => value.length <= max,
    message: message || `长度不能超过${max}位`,
  };
}

/**
 * 创建正则表达式验证器
 * @param pattern 正则表达式
 * @param message 错误消息
 * @returns 验证器
 */
export function pattern(pattern: RegExp, message: string) {
  return {
    validator: (value: string) => pattern.test(value),
    message,
  };
}

/**
 * 创建邮箱验证器
 * @param message 错误消息
 * @returns 验证器
 */
export function email(message: string = '请输入有效的邮箱地址') {
  return {
    validator: validateEmail,
    message,
  };
}

/**
 * 创建手机号验证器
 * @param message 错误消息
 * @returns 验证器
 */
export function phone(message: string = '请输入有效的手机号') {
  return {
    validator: validatePhone,
    message,
  };
}

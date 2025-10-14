import dayjs from 'dayjs';

/**
 * 格式化数字
 * @param value 数值
 * @param decimals 小数位数
 * @param thousandSeparator 千分位分隔符
 * @returns 格式化后的字符串
 */
export function formatNumber(
  value: number | string,
  decimals: number = 0,
  thousandSeparator: string = ','
): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0';

  const parts = num.toFixed(decimals).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandSeparator);
  
  return parts.join('.');
}

/**
 * 格式化货币
 * @param value 数值
 * @param currency 货币符号
 * @param decimals 小数位数
 * @returns 格式化后的货币字符串
 */
export function formatCurrency(
  value: number | string,
  currency: string = '¥',
  decimals: number = 2
): string {
  const formatted = formatNumber(value, decimals);
  return `${currency}${formatted}`;
}

/**
 * 格式化百分比
 * @param value 数值（0-1之间）
 * @param decimals 小数位数
 * @returns 格式化后的百分比字符串
 */
export function formatPercentage(
  value: number | string,
  decimals: number = 1
): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0%';
  
  return `${(num * 100).toFixed(decimals)}%`;
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

/**
 * 格式化时间
 * @param value 时间值
 * @param format 格式字符串
 * @returns 格式化后的时间字符串
 */
export function formatTime(
  value: string | number | Date | dayjs.Dayjs,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  if (!value) return '';
  return dayjs(value).format(format);
}

/**
 * 格式化相对时间
 * @param value 时间值
 * @returns 相对时间字符串
 */
export function formatRelativeTime(value: string | number | Date | dayjs.Dayjs): string {
  if (!value) return '';
  return dayjs(value).fromNow();
}

/**
 * 格式化手机号
 * @param phone 手机号
 * @returns 格式化后的手机号
 */
export function formatPhone(phone: string): string {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3');
  }
  
  return phone;
}

/**
 * 格式化身份证号
 * @param idCard 身份证号
 * @param mask 是否遮蔽中间部分
 * @returns 格式化后的身份证号
 */
export function formatIdCard(idCard: string, mask: boolean = false): string {
  if (!idCard) return '';
  
  if (mask && idCard.length === 18) {
    return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
  }
  
  return idCard;
}

/**
 * 格式化银行卡号
 * @param cardNumber 银行卡号
 * @param mask 是否遮蔽中间部分
 * @returns 格式化后的银行卡号
 */
export function formatBankCard(cardNumber: string, mask: boolean = false): string {
  if (!cardNumber) return '';
  
  const cleaned = cardNumber.replace(/\D/g, '');
  
  if (mask && cleaned.length >= 8) {
    const start = cleaned.slice(0, 4);
    const end = cleaned.slice(-4);
    const middle = '*'.repeat(cleaned.length - 8);
    return `${start} ${middle} ${end}`;
  }
  
  return cleaned.replace(/(\d{4})/g, '$1 ').trim();
}

/**
 * 格式化姓名（遮蔽）
 * @param name 姓名
 * @returns 遮蔽后的姓名
 */
export function formatNameMask(name: string): string {
  if (!name) return '';
  
  if (name.length <= 2) {
    return name.charAt(0) + '*';
  }
  
  return name.charAt(0) + '*'.repeat(name.length - 2) + name.charAt(name.length - 1);
}

/**
 * 格式化邮箱（遮蔽）
 * @param email 邮箱
 * @returns 遮蔽后的邮箱
 */
export function formatEmailMask(email: string): string {
  if (!email) return '';
  
  const [username, domain] = email.split('@');
  if (!username || !domain) return email;
  
  const maskedUsername = username.length > 2 
    ? username.charAt(0) + '*'.repeat(username.length - 2) + username.charAt(username.length - 1)
    : username.charAt(0) + '*';
    
  return `${maskedUsername}@${domain}`;
}

/**
 * 格式化地址（省略）
 * @param address 地址
 * @param maxLength 最大长度
 * @returns 省略后的地址
 */
export function formatAddress(address: string, maxLength: number = 20): string {
  if (!address) return '';
  
  if (address.length <= maxLength) {
    return address;
  }
  
  return address.slice(0, maxLength - 3) + '...';
}

/**
 * 格式化用户类型
 * @param userType 用户类型
 * @returns 用户类型显示名称
 */
export function formatUserType(userType: string): string {
  const typeMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  };
  
  return typeMap[userType] || userType;
}

/**
 * 格式化课程类型
 * @param courseType 课程类型
 * @returns 课程类型显示名称
 */
export function formatCourseType(courseType: string): string {
  const typeMap: Record<string, string> = {
    required: '必修课',
    elective: '选修课',
    public: '公共课',
    professional: '专业课',
  };
  
  return typeMap[courseType] || courseType;
}

/**
 * 格式化状态
 * @param status 状态值
 * @param statusMap 状态映射
 * @returns 状态显示名称
 */
export function formatStatus(
  status: string | number | boolean,
  statusMap?: Record<string, string>
): string {
  if (statusMap) {
    return statusMap[String(status)] || String(status);
  }
  
  // 默认布尔值映射
  if (typeof status === 'boolean') {
    return status ? '是' : '否';
  }
  
  // 默认数字状态映射
  const defaultMap: Record<string, string> = {
    '0': '禁用',
    '1': '启用',
    'true': '是',
    'false': '否',
    'active': '活跃',
    'inactive': '非活跃',
    'enabled': '启用',
    'disabled': '禁用',
  };
  
  return defaultMap[String(status)] || String(status);
}

/**
 * 格式化数组为字符串
 * @param array 数组
 * @param separator 分隔符
 * @param formatter 格式化函数
 * @returns 格式化后的字符串
 */
export function formatArray<T>(
  array: T[],
  separator: string = ', ',
  formatter?: (item: T) => string
): string {
  if (!Array.isArray(array) || array.length === 0) return '';
  
  const items = formatter ? array.map(formatter) : array.map(String);
  return items.join(separator);
}

/**
 * 格式化对象为键值对字符串
 * @param obj 对象
 * @param separator 分隔符
 * @param keyValueSeparator 键值分隔符
 * @returns 格式化后的字符串
 */
export function formatObject(
  obj: Record<string, any>,
  separator: string = ', ',
  keyValueSeparator: string = ': '
): string {
  if (!obj || typeof obj !== 'object') return '';
  
  const pairs = Object.entries(obj).map(([key, value]) => 
    `${key}${keyValueSeparator}${value}`
  );
  
  return pairs.join(separator);
}

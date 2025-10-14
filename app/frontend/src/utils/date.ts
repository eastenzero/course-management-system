import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import relativeTime from 'dayjs/plugin/relativeTime';
import weekOfYear from 'dayjs/plugin/weekOfYear';
import isoWeek from 'dayjs/plugin/isoWeek';
import 'dayjs/locale/zh-cn';

// 扩展dayjs插件
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);
dayjs.extend(weekOfYear);
dayjs.extend(isoWeek);
dayjs.locale('zh-cn');

export type DateInput = string | number | Date | dayjs.Dayjs;

/**
 * 格式化日期
 * @param date 日期
 * @param format 格式字符串
 * @returns 格式化后的日期字符串
 */
export function formatDate(
  date: DateInput,
  format: string = 'YYYY-MM-DD'
): string {
  if (!date) return '';
  return dayjs(date).format(format);
}

/**
 * 格式化时间
 * @param date 日期
 * @param format 格式字符串
 * @returns 格式化后的时间字符串
 */
export function formatDateTime(
  date: DateInput,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  if (!date) return '';
  return dayjs(date).format(format);
}

/**
 * 格式化相对时间
 * @param date 日期
 * @returns 相对时间字符串
 */
export function formatRelativeTime(date: DateInput): string {
  if (!date) return '';
  return dayjs(date).fromNow();
}

/**
 * 获取当前时间
 * @param format 格式字符串
 * @returns 当前时间字符串
 */
export function getCurrentTime(format?: string): string {
  return format ? dayjs().format(format) : dayjs().toISOString();
}

/**
 * 获取今天的开始时间
 * @returns 今天开始时间
 */
export function getStartOfToday(): dayjs.Dayjs {
  return dayjs().startOf('day');
}

/**
 * 获取今天的结束时间
 * @returns 今天结束时间
 */
export function getEndOfToday(): dayjs.Dayjs {
  return dayjs().endOf('day');
}

/**
 * 获取本周的开始时间
 * @returns 本周开始时间
 */
export function getStartOfWeek(): dayjs.Dayjs {
  return dayjs().startOf('week');
}

/**
 * 获取本周的结束时间
 * @returns 本周结束时间
 */
export function getEndOfWeek(): dayjs.Dayjs {
  return dayjs().endOf('week');
}

/**
 * 获取本月的开始时间
 * @returns 本月开始时间
 */
export function getStartOfMonth(): dayjs.Dayjs {
  return dayjs().startOf('month');
}

/**
 * 获取本月的结束时间
 * @returns 本月结束时间
 */
export function getEndOfMonth(): dayjs.Dayjs {
  return dayjs().endOf('month');
}

/**
 * 计算两个日期之间的差值
 * @param date1 日期1
 * @param date2 日期2
 * @param unit 单位
 * @returns 差值
 */
export function dateDiff(
  date1: DateInput,
  date2: DateInput,
  unit: dayjs.UnitType = 'day'
): number {
  return dayjs(date1).diff(dayjs(date2), unit);
}

/**
 * 添加时间
 * @param date 日期
 * @param amount 数量
 * @param unit 单位
 * @returns 新日期
 */
export function addTime(
  date: DateInput,
  amount: number,
  unit: dayjs.ManipulateType
): dayjs.Dayjs {
  return dayjs(date).add(amount, unit);
}

/**
 * 减少时间
 * @param date 日期
 * @param amount 数量
 * @param unit 单位
 * @returns 新日期
 */
export function subtractTime(
  date: DateInput,
  amount: number,
  unit: dayjs.ManipulateType
): dayjs.Dayjs {
  return dayjs(date).subtract(amount, unit);
}

/**
 * 判断是否为今天
 * @param date 日期
 * @returns 是否为今天
 */
export function isToday(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs(), 'day');
}

/**
 * 判断是否为昨天
 * @param date 日期
 * @returns 是否为昨天
 */
export function isYesterday(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs().subtract(1, 'day'), 'day');
}

/**
 * 判断是否为明天
 * @param date 日期
 * @returns 是否为明天
 */
export function isTomorrow(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs().add(1, 'day'), 'day');
}

/**
 * 判断是否为本周
 * @param date 日期
 * @returns 是否为本周
 */
export function isThisWeek(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs(), 'week');
}

/**
 * 判断是否为本月
 * @param date 日期
 * @returns 是否为本月
 */
export function isThisMonth(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs(), 'month');
}

/**
 * 判断是否为本年
 * @param date 日期
 * @returns 是否为本年
 */
export function isThisYear(date: DateInput): boolean {
  return dayjs(date).isSame(dayjs(), 'year');
}

/**
 * 判断日期是否在范围内
 * @param date 日期
 * @param start 开始日期
 * @param end 结束日期
 * @returns 是否在范围内
 */
export function isDateInRange(
  date: DateInput,
  start: DateInput,
  end: DateInput
): boolean {
  const d = dayjs(date);
  return d.isAfter(dayjs(start)) && d.isBefore(dayjs(end));
}

/**
 * 获取星期几
 * @param date 日期
 * @param format 格式（'short' | 'long' | 'number'）
 * @returns 星期几
 */
export function getWeekday(
  date: DateInput,
  format: 'short' | 'long' | 'number' = 'long'
): string | number {
  const d = dayjs(date);
  
  if (format === 'number') {
    return d.day(); // 0-6，0为周日
  }
  
  const weekdays = {
    short: ['日', '一', '二', '三', '四', '五', '六'],
    long: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
  };
  
  return weekdays[format][d.day()];
}

/**
 * 获取月份名称
 * @param date 日期
 * @param format 格式（'short' | 'long' | 'number'）
 * @returns 月份名称
 */
export function getMonthName(
  date: DateInput,
  format: 'short' | 'long' | 'number' = 'long'
): string | number {
  const d = dayjs(date);
  
  if (format === 'number') {
    return d.month() + 1; // 1-12
  }
  
  const months = {
    short: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
    long: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
  };
  
  return months[format][d.month()];
}

/**
 * 获取学期信息
 * @param date 日期
 * @returns 学期信息
 */
export function getSemesterInfo(date: DateInput = new Date()): {
  year: number;
  semester: number;
  semesterName: string;
} {
  const d = dayjs(date);
  const month = d.month() + 1; // 1-12
  const year = d.year();
  
  // 假设9月-1月为第一学期，2月-8月为第二学期
  if (month >= 9 || month <= 1) {
    return {
      year: month >= 9 ? year : year - 1,
      semester: 1,
      semesterName: '第一学期',
    };
  } else {
    return {
      year,
      semester: 2,
      semesterName: '第二学期',
    };
  }
}

/**
 * 获取学年信息
 * @param date 日期
 * @returns 学年信息
 */
export function getAcademicYear(date: DateInput = new Date()): {
  startYear: number;
  endYear: number;
  academicYear: string;
} {
  const d = dayjs(date);
  const month = d.month() + 1;
  const year = d.year();
  
  const startYear = month >= 9 ? year : year - 1;
  const endYear = startYear + 1;
  
  return {
    startYear,
    endYear,
    academicYear: `${startYear}-${endYear}`,
  };
}

/**
 * 获取时间段描述
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @returns 时间段描述
 */
export function getTimeRangeDescription(
  startTime: DateInput,
  endTime: DateInput
): string {
  const start = dayjs(startTime);
  const end = dayjs(endTime);
  
  if (start.isSame(end, 'day')) {
    return `${start.format('YYYY-MM-DD')} ${start.format('HH:mm')}-${end.format('HH:mm')}`;
  } else {
    return `${start.format('YYYY-MM-DD HH:mm')} - ${end.format('YYYY-MM-DD HH:mm')}`;
  }
}

/**
 * 解析时间字符串为时分
 * @param timeStr 时间字符串（如 "14:30"）
 * @returns 时分对象
 */
export function parseTimeString(timeStr: string): { hour: number; minute: number } | null {
  const match = timeStr.match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return null;
  
  const hour = parseInt(match[1], 10);
  const minute = parseInt(match[2], 10);
  
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
    return null;
  }
  
  return { hour, minute };
}

/**
 * 格式化时间段
 * @param startTime 开始时间（如 "08:00"）
 * @param endTime 结束时间（如 "09:50"）
 * @returns 格式化的时间段
 */
export function formatTimeRange(startTime: string, endTime: string): string {
  return `${startTime}-${endTime}`;
}

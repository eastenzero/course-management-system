/**
 * 导出工具函数
 */

/**
 * 下载文件
 * @param blob 文件数据
 * @param filename 文件名
 */
export function downloadFile(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * 导出为CSV文件
 * @param data 数据数组
 * @param headers 表头配置
 * @param filename 文件名
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  headers: Array<{ key: keyof T; label: string }>,
  filename: string = 'export.csv'
): void {
  if (!data.length) return;

  // 构建CSV内容
  const csvContent = [
    // 表头
    headers.map(header => `"${header.label}"`).join(','),
    // 数据行
    ...data.map(row =>
      headers.map(header => {
        const value = row[header.key];
        // 处理特殊字符和换行符
        const stringValue = String(value || '').replace(/"/g, '""');
        return `"${stringValue}"`;
      }).join(',')
    ),
  ].join('\n');

  // 添加BOM以支持中文
  const bom = '\uFEFF';
  const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' });
  
  downloadFile(blob, filename);
}

/**
 * 导出为Excel文件（简单版本，使用CSV格式）
 * @param data 数据数组
 * @param headers 表头配置
 * @param filename 文件名
 */
export function exportToExcel<T extends Record<string, any>>(
  data: T[],
  headers: Array<{ key: keyof T; label: string }>,
  filename: string = 'export.xlsx'
): void {
  // 这里使用CSV格式，实际项目中可以使用xlsx库
  const csvFilename = filename.replace(/\.xlsx?$/, '.csv');
  exportToCSV(data, headers, csvFilename);
}

/**
 * 导出为JSON文件
 * @param data 数据
 * @param filename 文件名
 */
export function exportToJSON(data: any, filename: string = 'export.json'): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  downloadFile(blob, filename);
}

/**
 * 导出为文本文件
 * @param content 文本内容
 * @param filename 文件名
 */
export function exportToText(content: string, filename: string = 'export.txt'): void {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  downloadFile(blob, filename);
}

/**
 * 导出表格数据
 * @param tableData 表格数据
 * @param options 导出选项
 */
export function exportTableData<T extends Record<string, any>>(
  tableData: T[],
  options: {
    headers: Array<{ key: keyof T; label: string; formatter?: (value: any) => string }>;
    filename?: string;
    format?: 'csv' | 'excel' | 'json';
    title?: string;
  }
): void {
  const { headers, filename, format = 'csv', title } = options;
  
  if (!tableData.length) {
    console.warn('没有数据可导出');
    return;
  }

  // 处理数据格式化
  const processedData = tableData.map(row => {
    const processedRow: Record<string, any> = {};
    headers.forEach(header => {
      const value = row[header.key];
      processedRow[header.key] = header.formatter ? header.formatter(value) : value;
    });
    return processedRow;
  });

  const defaultFilename = `${title || 'export'}_${new Date().toISOString().slice(0, 10)}`;

  switch (format) {
    case 'excel':
      exportToExcel(processedData, headers, filename || `${defaultFilename}.xlsx`);
      break;
    case 'json':
      exportToJSON(processedData, filename || `${defaultFilename}.json`);
      break;
    default:
      exportToCSV(processedData, headers, filename || `${defaultFilename}.csv`);
  }
}

/**
 * 导出课程数据
 * @param courses 课程数据
 * @param format 导出格式
 */
export function exportCourses(
  courses: any[],
  format: 'csv' | 'excel' | 'json' = 'csv'
): void {
  const headers = [
    { key: 'code', label: '课程代码' },
    { key: 'name', label: '课程名称' },
    { key: 'credits', label: '学分' },
    { key: 'department', label: '院系' },
    { key: 'course_type_display', label: '课程类型' },
    { key: 'max_students', label: '最大人数' },
    { key: 'current_enrollment', label: '当前选课人数' },
    { key: 'teachers_count', label: '授课教师数量' },
    { 
      key: 'is_active', 
      label: '状态',
      formatter: (value: boolean) => value ? '启用' : '禁用'
    },
  ];

  exportTableData(courses, {
    headers,
    format,
    title: '课程列表',
  });
}

/**
 * 导出用户数据
 * @param users 用户数据
 * @param format 导出格式
 */
export function exportUsers(
  users: any[],
  format: 'csv' | 'excel' | 'json' = 'csv'
): void {
  const headers = [
    { key: 'username', label: '用户名' },
    { key: 'email', label: '邮箱' },
    { key: 'first_name', label: '姓' },
    { key: 'last_name', label: '名' },
    { key: 'user_type_display', label: '用户类型' },
    { key: 'employee_id', label: '工号' },
    { key: 'student_id', label: '学号' },
    { key: 'department', label: '院系' },
    { 
      key: 'is_active', 
      label: '状态',
      formatter: (value: boolean) => value ? '启用' : '禁用'
    },
    { 
      key: 'date_joined', 
      label: '创建时间',
      formatter: (value: string) => new Date(value).toLocaleDateString()
    },
  ];

  exportTableData(users, {
    headers,
    format,
    title: '用户列表',
  });
}

/**
 * 导出教室数据
 * @param classrooms 教室数据
 * @param format 导出格式
 */
export function exportClassrooms(
  classrooms: any[],
  format: 'csv' | 'excel' | 'json' = 'csv'
): void {
  const headers = [
    { key: 'name', label: '教室名称' },
    { key: 'building_name', label: '楼栋' },
    { key: 'room_number', label: '房间号' },
    { key: 'floor', label: '楼层' },
    { key: 'capacity', label: '容量' },
    { key: 'room_type_display', label: '教室类型' },
    { 
      key: 'is_available', 
      label: '可用状态',
      formatter: (value: boolean) => value ? '可用' : '不可用'
    },
    { 
      key: 'is_active', 
      label: '启用状态',
      formatter: (value: boolean) => value ? '启用' : '禁用'
    },
  ];

  exportTableData(classrooms, {
    headers,
    format,
    title: '教室列表',
  });
}

/**
 * 导出课程表数据
 * @param schedules 课程表数据
 * @param format 导出格式
 */
export function exportSchedules(
  schedules: any[],
  format: 'csv' | 'excel' | 'json' = 'csv'
): void {
  const headers = [
    { key: 'course_name', label: '课程名称' },
    { key: 'course_code', label: '课程代码' },
    { key: 'teacher_name', label: '授课教师' },
    { key: 'classroom_name', label: '教室' },
    { 
      key: 'day_of_week', 
      label: '星期',
      formatter: (value: number) => {
        const days = ['日', '一', '二', '三', '四', '五', '六'];
        return `星期${days[value]}`;
      }
    },
    { key: 'start_time', label: '开始时间' },
    { key: 'end_time', label: '结束时间' },
    { key: 'weeks', label: '周次' },
    { key: 'semester', label: '学期' },
  ];

  exportTableData(schedules, {
    headers,
    format,
    title: '课程表',
  });
}

/**
 * 批量导出功能
 * @param exports 导出配置数组
 */
export function batchExport(
  exports: Array<{
    data: any[];
    headers: Array<{ key: string; label: string; formatter?: (value: any) => string }>;
    filename: string;
    format?: 'csv' | 'excel' | 'json';
  }>
): void {
  exports.forEach(exportConfig => {
    const { data, headers, filename, format = 'csv' } = exportConfig;
    exportTableData(data, { headers, filename, format });
  });
}

/**
 * 创建导出按钮配置
 * @param data 数据
 * @param headers 表头
 * @param title 标题
 * @returns 按钮配置
 */
export function createExportButtons<T extends Record<string, any>>(
  data: T[],
  headers: Array<{ key: keyof T; label: string; formatter?: (value: any) => string }>,
  title: string = 'export'
) {
  return [
    {
      key: 'csv',
      label: '导出CSV',
      onClick: () => exportTableData(data, { headers, format: 'csv', title }),
    },
    {
      key: 'excel',
      label: '导出Excel',
      onClick: () => exportTableData(data, { headers, format: 'excel', title }),
    },
    {
      key: 'json',
      label: '导出JSON',
      onClick: () => exportTableData(data, { headers, format: 'json', title }),
    },
  ];
}

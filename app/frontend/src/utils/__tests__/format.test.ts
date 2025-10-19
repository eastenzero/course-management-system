import {
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatFileSize,
  formatTime,
  formatPhone,
  formatIdCard,
  formatUserType,
  formatCourseType,
  formatStatus,
} from '../format';

describe('format utils', () => {
  describe('formatNumber', () => {
    it('should format numbers with default settings', () => {
      expect(formatNumber(1234)).toBe('1,234');
      expect(formatNumber(1234.56)).toBe('1,235');
      expect(formatNumber(1234.56, 2)).toBe('1,234.56');
    });

    it('should handle string input', () => {
      expect(formatNumber('1234.56', 2)).toBe('1,234.56');
      expect(formatNumber('invalid')).toBe('0');
    });

    it('should handle custom thousand separator', () => {
      expect(formatNumber(1234567, 0, ' ')).toBe('1 234 567');
    });

    it('should handle zero and negative numbers', () => {
      expect(formatNumber(0)).toBe('0');
      expect(formatNumber(-1234.56, 2)).toBe('-1,234.56');
    });
  });

  describe('formatCurrency', () => {
    it('should format currency with default settings', () => {
      expect(formatCurrency(1234.56)).toBe('¥1,234.56');
    });

    it('should handle custom currency symbol', () => {
      expect(formatCurrency(1234.56, '$')).toBe('$1,234.56');
    });

    it('should handle custom decimal places', () => {
      expect(formatCurrency(1234.567, '¥', 3)).toBe('¥1,234.567');
    });
  });

  describe('formatPercentage', () => {
    it('should format percentage correctly', () => {
      expect(formatPercentage(0.1234)).toBe('12.3%');
      expect(formatPercentage(0.1234, 2)).toBe('12.34%');
    });

    it('should handle string input', () => {
      expect(formatPercentage('0.5')).toBe('50.0%');
      expect(formatPercentage('invalid')).toBe('0%');
    });

    it('should handle edge cases', () => {
      expect(formatPercentage(0)).toBe('0.0%');
      expect(formatPercentage(1)).toBe('100.0%');
    });
  });

  describe('formatFileSize', () => {
    it('should format file sizes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should handle custom decimal places', () => {
      expect(formatFileSize(1536, 1)).toBe('1.5 KB');
      expect(formatFileSize(1536, 3)).toBe('1.500 KB');
    });
  });

  describe('formatTime', () => {
    it('should format time with default format', () => {
      const date = new Date('2024-01-01T12:30:45');
      expect(formatTime(date)).toBe('2024-01-01 12:30:45');
    });

    it('should handle custom format', () => {
      const date = new Date('2024-01-01T12:30:45');
      expect(formatTime(date, 'YYYY-MM-DD')).toBe('2024-01-01');
      expect(formatTime(date, 'HH:mm:ss')).toBe('12:30:45');
    });

    it('should handle empty input', () => {
      expect(formatTime('')).toBe('');
      expect(formatTime(null as any)).toBe('');
    });
  });

  describe('formatPhone', () => {
    it('should format phone numbers correctly', () => {
      expect(formatPhone('13800138000')).toBe('138 0013 8000');
    });

    it('should handle invalid phone numbers', () => {
      expect(formatPhone('123')).toBe('123');
      expect(formatPhone('')).toBe('');
    });

    it('should clean non-digit characters', () => {
      expect(formatPhone('138-0013-8000')).toBe('138 0013 8000');
    });
  });

  describe('formatIdCard', () => {
    it('should format ID card without mask', () => {
      const idCard = '123456789012345678';
      expect(formatIdCard(idCard)).toBe(idCard);
    });

    it('should format ID card with mask', () => {
      const idCard = '123456789012345678';
      expect(formatIdCard(idCard, true)).toBe('123456********5678');
    });

    it('should handle empty input', () => {
      expect(formatIdCard('')).toBe('');
    });

    it('should handle short ID cards', () => {
      expect(formatIdCard('123456', true)).toBe('123456');
    });
  });

  describe('formatUserType', () => {
    it('should format user types correctly', () => {
      expect(formatUserType('admin')).toBe('管理员');
      expect(formatUserType('teacher')).toBe('教师');
      expect(formatUserType('student')).toBe('学生');
    });

    it('should return original value for unknown types', () => {
      expect(formatUserType('unknown')).toBe('unknown');
    });
  });

  describe('formatCourseType', () => {
    it('should format course types correctly', () => {
      expect(formatCourseType('required')).toBe('必修课');
      expect(formatCourseType('elective')).toBe('选修课');
      expect(formatCourseType('public')).toBe('公共课');
      expect(formatCourseType('professional')).toBe('专业课');
    });

    it('should return original value for unknown types', () => {
      expect(formatCourseType('unknown')).toBe('unknown');
    });
  });

  describe('formatStatus', () => {
    it('should format boolean status', () => {
      expect(formatStatus(true)).toBe('是');
      expect(formatStatus(false)).toBe('否');
    });

    it('should format with custom status map', () => {
      const statusMap = {
        '1': '启用',
        '0': '禁用',
      };
      expect(formatStatus('1', statusMap)).toBe('启用');
      expect(formatStatus('0', statusMap)).toBe('禁用');
    });

    it('should format default number status', () => {
      expect(formatStatus(1)).toBe('启用');
      expect(formatStatus(0)).toBe('禁用');
    });

    it('should format default string status', () => {
      expect(formatStatus('active')).toBe('活跃');
      expect(formatStatus('inactive')).toBe('非活跃');
      expect(formatStatus('enabled')).toBe('启用');
      expect(formatStatus('disabled')).toBe('禁用');
    });

    it('should return original value for unknown status', () => {
      expect(formatStatus('unknown')).toBe('unknown');
    });
  });
});

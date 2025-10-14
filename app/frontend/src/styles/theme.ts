import { ThemeConfig } from 'antd';

// 现代化教育平台主题配置
export const modernTheme: ThemeConfig = {
  token: {
    colorPrimary: '#667eea',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#4facfe',
    colorText: '#262626',
    colorTextSecondary: '#595959',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#fafafa',
    colorBorder: '#e8e8e8',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
    fontSize: 14,
    controlHeight: 36,
    controlHeightLG: 44,
    controlHeightSM: 28,
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      headerHeight: 64,
      siderBg: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
    },
    Button: {
      borderRadius: 8,
      controlHeight: 36,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 36,
    },
    Card: {
      headerBg: 'transparent',
      paddingLG: 24,
    },
  },
};

// 教师端专用主题
export const teacherTheme: ThemeConfig = {
  ...modernTheme,
  token: {
    ...modernTheme.token,
    colorPrimary: '#667eea',
  },
};

// 学生端专用主题
export const studentTheme: ThemeConfig = {
  ...modernTheme,
  token: {
    ...modernTheme.token,
    colorPrimary: '#4facfe',
  },
};



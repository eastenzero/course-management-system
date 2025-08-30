export { default as LineChart } from './LineChart';
export { default as BarChart } from './BarChart';
export { default as PieChart } from './PieChart';

// 图表数据类型
export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

// 图表颜色主题
export const chartColors = {
  primary: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
  blue: ['#1890ff', '#40a9ff', '#69c0ff', '#91d5ff', '#bae7ff'],
  green: ['#52c41a', '#73d13d', '#95de64', '#b7eb8f', '#d9f7be'],
  orange: ['#faad14', '#ffc53d', '#ffd666', '#ffe58f', '#fff1b8'],
  red: ['#f5222d', '#ff4d4f', '#ff7875', '#ffa39e', '#ffccc7'],
  purple: ['#722ed1', '#9254de', '#b37feb', '#d3adf7', '#efdbff'],
};

// 图表通用配置
export const chartConfig = {
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
  tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: 'transparent',
    textStyle: {
      color: '#fff',
    },
  },
  legend: {
    textStyle: {
      color: '#666',
    },
  },
};

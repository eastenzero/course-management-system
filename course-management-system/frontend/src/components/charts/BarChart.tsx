import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { Spin } from 'antd';

interface DataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

interface BarChartProps {
  data: DataPoint[];
  title?: string;
  xAxisKey?: string;
  yAxisKey?: string;
  height?: number;
  loading?: boolean;
  color?: string[];
  horizontal?: boolean;
  showGrid?: boolean;
  showLegend?: boolean;
  showLabel?: boolean;
  onBarClick?: (data: DataPoint) => void;
}

const BarChart: React.FC<BarChartProps> = ({
  data,
  title,
  xAxisKey = 'name',
  yAxisKey = 'value',
  height = 400,
  loading = false,
  color = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
  horizontal = false,
  showGrid = true,
  showLegend = true,
  showLabel = false,
  onBarClick,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || loading) return;

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const option: echarts.EChartsOption = {
      title: title ? {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal',
        },
      } : undefined,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: (params: any) => {
          if (Array.isArray(params)) {
            const param = params[0];
            return `${param.name}<br/>${param.seriesName}: ${param.value}`;
          }
          return `${params.name}<br/>${params.seriesName}: ${params.value}`;
        },
      },
      legend: showLegend ? {
        data: ['数据'],
        bottom: 10,
      } : undefined,
      grid: showGrid ? {
        left: '3%',
        right: '4%',
        bottom: showLegend ? '15%' : '3%',
        containLabel: true,
      } : undefined,
      xAxis: {
        type: horizontal ? 'value' : 'category',
        data: horizontal ? undefined : data.map(item => item[xAxisKey]),
        axisLine: {
          lineStyle: {
            color: '#d9d9d9',
          },
        },
        axisLabel: {
          color: '#666',
          interval: 0,
          rotate: horizontal ? 0 : (data.length > 10 ? 45 : 0),
        },
        splitLine: horizontal ? {
          lineStyle: {
            color: '#f0f0f0',
          },
        } : undefined,
      },
      yAxis: {
        type: horizontal ? 'category' : 'value',
        data: horizontal ? data.map(item => item[xAxisKey]) : undefined,
        axisLine: {
          lineStyle: {
            color: '#d9d9d9',
          },
        },
        axisLabel: {
          color: '#666',
        },
        splitLine: !horizontal ? {
          lineStyle: {
            color: '#f0f0f0',
          },
        } : undefined,
      },
      series: [
        {
          name: '数据',
          type: 'bar',
          data: data.map(item => ({
            name: item[xAxisKey],
            value: item[yAxisKey],
            itemStyle: {
              color: color[0],
            },
          })),
          label: showLabel ? {
            show: true,
            position: horizontal ? 'right' : 'top',
            color: '#666',
          } : undefined,
          emphasis: {
            focus: 'series',
            itemStyle: {
              color: color[1] || '#40a9ff',
            },
          },
          barWidth: '60%',
        },
      ],
    };

    chartInstance.current.setOption(option);

    // 点击事件
    if (onBarClick) {
      chartInstance.current.off('click');
      chartInstance.current.on('click', (params: any) => {
        const dataIndex = params.dataIndex;
        if (dataIndex >= 0 && dataIndex < data.length) {
          onBarClick(data[dataIndex]);
        }
      });
    }

    // 响应式
    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, title, xAxisKey, yAxisKey, color, horizontal, showGrid, showLegend, showLabel, onBarClick, loading]);

  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }
    };
  }, []);

  if (loading) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div
      ref={chartRef}
      style={{
        width: '100%',
        height,
      }}
    />
  );
};

export default BarChart;

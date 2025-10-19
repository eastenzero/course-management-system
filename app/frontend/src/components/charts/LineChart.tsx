import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { Spin } from 'antd';

interface DataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

interface LineChartProps {
  data: DataPoint[];
  title?: string;
  xAxisKey?: string;
  yAxisKey?: string;
  height?: number;
  loading?: boolean;
  color?: string[];
  smooth?: boolean;
  showArea?: boolean;
  showGrid?: boolean;
  showLegend?: boolean;
  onPointClick?: (data: DataPoint) => void;
}

const LineChart: React.FC<LineChartProps> = ({
  data,
  title,
  xAxisKey = 'name',
  yAxisKey = 'value',
  height = 400,
  loading = false,
  color = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'],
  smooth = true,
  showArea = false,
  showGrid = true,
  showLegend = true,
  onPointClick,
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
          type: 'cross',
          label: {
            backgroundColor: '#6a7985',
          },
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
        type: 'category',
        boundaryGap: false,
        data: data.map(item => item[xAxisKey]),
        axisLine: {
          lineStyle: {
            color: '#d9d9d9',
          },
        },
        axisLabel: {
          color: '#666',
        },
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#d9d9d9',
          },
        },
        axisLabel: {
          color: '#666',
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0',
          },
        },
      },
      series: [
        {
          name: '数据',
          type: 'line',
          smooth: smooth,
          data: data.map(item => item[yAxisKey]),
          itemStyle: {
            color: color[0],
          },
          lineStyle: {
            color: color[0],
            width: 2,
          },
          areaStyle: showArea ? {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: color[0] + '40',
              },
              {
                offset: 1,
                color: color[0] + '10',
              },
            ]),
          } : undefined,
          emphasis: {
            focus: 'series',
          },
        },
      ],
    };

    chartInstance.current.setOption(option);

    // 点击事件
    if (onPointClick) {
      chartInstance.current.off('click');
      chartInstance.current.on('click', (params: any) => {
        const dataIndex = params.dataIndex;
        if (dataIndex >= 0 && dataIndex < data.length) {
          onPointClick(data[dataIndex]);
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
  }, [data, title, xAxisKey, yAxisKey, color, smooth, showArea, showGrid, showLegend, onPointClick, loading]);

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

export default LineChart;

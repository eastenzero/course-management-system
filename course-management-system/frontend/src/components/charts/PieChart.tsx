import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { Spin } from 'antd';

interface DataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

interface PieChartProps {
  data: DataPoint[];
  title?: string;
  height?: number;
  loading?: boolean;
  color?: string[];
  showLegend?: boolean;
  showLabel?: boolean;
  showPercentage?: boolean;
  radius?: string | [string, string];
  center?: [string, string];
  roseType?: boolean;
  onSliceClick?: (data: DataPoint) => void;
}

const PieChart: React.FC<PieChartProps> = ({
  data,
  title,
  height = 400,
  loading = false,
  color = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#eb2f96', '#13c2c2', '#fa8c16'],
  showLegend = true,
  showLabel = true,
  showPercentage = true,
  radius = ['40%', '70%'],
  center = ['50%', '50%'],
  roseType = false,
  onSliceClick,
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
        top: 20,
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal',
        },
      } : undefined,
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const percent = params.percent;
          return `${params.name}<br/>${params.seriesName}: ${params.value} (${percent}%)`;
        },
      },
      legend: showLegend ? {
        type: 'scroll',
        orient: 'vertical',
        right: 10,
        top: 20,
        bottom: 20,
        data: data.map(item => item.name),
        textStyle: {
          fontSize: 12,
        },
      } : undefined,
      series: [
        {
          name: '数据',
          type: 'pie',
          radius: radius,
          center: center,
          roseType: roseType ? 'radius' : undefined,
          data: data.map((item, index) => ({
            name: item.name,
            value: item.value,
            itemStyle: {
              color: color[index % color.length],
            },
          })),
          label: showLabel ? {
            show: true,
            formatter: showPercentage ? '{b}: {c} ({d}%)' : '{b}: {c}',
            fontSize: 12,
          } : {
            show: false,
          },
          labelLine: showLabel ? {
            show: true,
          } : {
            show: false,
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
            },
          },
          animationType: 'scale',
          animationEasing: 'elasticOut',
          animationDelay: (_idx: number) => Math.random() * 200,
        },
      ],
    };

    chartInstance.current.setOption(option);

    // 点击事件
    if (onSliceClick) {
      chartInstance.current.off('click');
      chartInstance.current.on('click', (params: any) => {
        const dataIndex = params.dataIndex;
        if (dataIndex >= 0 && dataIndex < data.length) {
          onSliceClick(data[dataIndex]);
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
  }, [data, title, color, showLegend, showLabel, showPercentage, radius, center, roseType, onSliceClick, loading]);

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

export default PieChart;

import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Select,
  Row,
  Col,
  Tabs,
  Table,
  Tag,
  Button,
  Space,
  message,
  Modal,
  Checkbox,
} from 'antd';
import {
  CalendarOutlined,
  TableOutlined,
  PrinterOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { scheduleAPI } from '../../services/api';
import { simpleScheduleAPI } from '../../services/simpleScheduleAPI';

const { Title } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

interface Schedule {
  id: string;
  courseCode: string;
  courseName: string;
  teacher: string;
  classroom: string;
  dayOfWeek: number;
  startTime: string;
  endTime: string;
  weeks: string;
  semester: string;
}

const ScheduleViewPage: React.FC = () => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedSemester, setSelectedSemester] = useState('2024春');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // 获取真实的排课数据
  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        setLoading(true);
        const response = await simpleScheduleAPI.getSchedules({
        semester: selectedSemester,
        page: currentPage,
        page_size: pageSize,
      });
        
        if (response.data && response.data.results) {
          // 直接使用mockScheduleAPI返回的数据格式
          const scheduleData = response.data.results || [];
          setSchedules(scheduleData);
        }
      } catch (error) {
        console.error('获取排课数据失败:', error);
        message.error('获取排课数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchSchedules();
  }, [selectedSemester]);

  const weekDays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const timeSlots = [
    '08:00-09:40',
    '10:00-11:40',
    '14:00-15:40',
    '16:00-17:40',
    '19:00-20:40',
  ];

  const columns = [
    {
      title: '课程代码',
      dataIndex: 'courseCode',
      key: 'courseCode',
      width: 120,
    },
    {
      title: '课程名称',
      dataIndex: 'courseName',
      key: 'courseName',
      width: 150,
    },
    {
      title: '授课教师',
      dataIndex: 'teacher',
      key: 'teacher',
      width: 120,
    },
    {
      title: '教室',
      dataIndex: 'classroom',
      key: 'classroom',
      width: 100,
    },
    {
      title: '星期',
      dataIndex: 'dayOfWeek',
      key: 'dayOfWeek',
      width: 80,
      render: (day: number) => weekDays[day],
    },
    {
      title: '时间',
      key: 'time',
      width: 150,
      render: (record: Schedule) => `${record.startTime}-${record.endTime}`,
    },
    {
      title: '周次',
      dataIndex: 'weeks',
      key: 'weeks',
      width: 100,
    },
    {
      title: '学期',
      dataIndex: 'semester',
      key: 'semester',
      width: 100,
      render: (semester: string) => (
        <Tag color="blue">{semester}</Tag>
      ),
    },
  ];

  // 生成课程表视图
  const generateScheduleGrid = () => {
    const grid: any[][] = [];

    // 初始化网格
    for (let i = 0; i < timeSlots.length; i++) {
      grid[i] = new Array(8).fill(null);
    }

    // 填充课程数据
    schedules
      .filter(schedule => schedule.semester === selectedSemester)
      .forEach(schedule => {
        const timeIndex = timeSlots.findIndex(slot =>
          slot.startsWith(schedule.startTime.substring(0, 5))
        );
        if (timeIndex !== -1) {
          grid[timeIndex][schedule.dayOfWeek] = schedule;
        }
      });

    return grid;
  };

  const scheduleGrid = generateScheduleGrid();
  const filteredSchedules = schedules.filter(schedule => schedule.semester === selectedSemester);

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    Modal.confirm({
      title: '导出课程表',
      content: (
        <div>
          <p>请选择导出格式：</p>
          <Space direction="vertical">
            <Button
              type="primary"
              onClick={() => exportToExcel()}
              style={{ width: '100%' }}
            >
              导出为 Excel (.xlsx)
            </Button>
            <Button
              onClick={() => exportToPDF()}
              style={{ width: '100%' }}
            >
              导出为 PDF (.pdf)
            </Button>
            <Button
              onClick={() => exportToCSV()}
              style={{ width: '100%' }}
            >
              导出为 CSV (.csv)
            </Button>
          </Space>
        </div>
      ),
      footer: null,
      width: 400,
    });
  };

  const exportToExcel = async () => {
    try {
      message.loading('正在生成Excel文件...', 0);

      // 调用后端API导出Excel
      const response = await scheduleAPI.exportSchedules({
        format: 'excel',
        semester: selectedSemester,
        include_weekend: false,
        group_by: 'teacher'
      });

      // 创建下载链接
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `课程表_${selectedSemester}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.destroy();
      message.success('Excel文件导出成功');
    } catch (error) {
      message.destroy();
      console.error('导出Excel失败:', error);
      message.error('导出Excel失败');
    }
  };

  const exportToPDF = async () => {
    try {
      message.loading('正在生成PDF文件...', 0);

      // 调用后端API导出PDF
      const response = await scheduleAPI.exportSchedules({
        format: 'pdf',
        semester: selectedSemester,
        include_weekend: false,
        group_by: 'teacher'
      });

      // 创建下载链接
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `课程表_${selectedSemester}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.destroy();
      message.success('PDF文件导出成功');
    } catch (error) {
      message.destroy();
      console.error('导出PDF失败:', error);
      message.error('导出PDF失败');
    }
  };

  const exportToCSV = async () => {
    try {
      message.loading('正在生成CSV文件...', 0);

      // 调用后端API导出CSV
      const response = await scheduleAPI.exportSchedules({
        format: 'csv',
        semester: selectedSemester,
        include_weekend: false,
        group_by: 'teacher'
      });

      // 创建下载链接
      const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `课程表_${selectedSemester}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.destroy();
      message.success('CSV文件导出成功');
    } catch (error) {
      message.destroy();
      console.error('导出CSV失败:', error);
      message.error('导出CSV失败');
    }
  };

  return (
    <div className="schedule-view-page">
      <div className="page-header">
        <Title level={2}>课程表查看</Title>
        <p>查看当前学期的课程安排</p>
      </div>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Select
              value={selectedSemester}
              onChange={setSelectedSemester}
              style={{ width: '100%' }}
              placeholder="选择学期"
            >
              <Option value="2024-1">2024年春季学期</Option>
              <Option value="2024-2">2024年秋季学期</Option>
              <Option value="2025-1">2025年春季学期</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={16} style={{ textAlign: 'right' }}>
            <Space>
              <Button 
                icon={<PrinterOutlined />}
                onClick={handlePrint}
              >
                打印课程表
              </Button>
              <Button 
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleExport}
              >
                导出课程表
              </Button>
            </Space>
          </Col>
        </Row>

        <Tabs defaultActiveKey="grid">
          <TabPane 
            tab={
              <span>
                <CalendarOutlined />
                课程表视图
              </span>
            } 
            key="grid"
          >
            <div style={{ overflowX: 'auto' }}>
              <table style={{ 
                width: '100%', 
                border: '1px solid #d9d9d9', 
                borderCollapse: 'collapse',
                minWidth: '800px'
              }}>
                <thead>
                  <tr>
                    <th style={{ 
                      border: '1px solid #d9d9d9', 
                      padding: '12px 8px', 
                      background: '#fafafa',
                      fontWeight: 'bold',
                      textAlign: 'center'
                    }}>
                      时间
                    </th>
                    {weekDays.slice(1).map(day => (
                      <th key={day} style={{ 
                        border: '1px solid #d9d9d9', 
                        padding: '12px 8px', 
                        background: '#fafafa',
                        fontWeight: 'bold',
                        textAlign: 'center'
                      }}>
                        {day}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timeSlots.map((timeSlot, timeIndex) => (
                    <tr key={timeSlot}>
                      <td style={{ 
                        border: '1px solid #d9d9d9', 
                        padding: '12px 8px', 
                        background: '#fafafa', 
                        fontWeight: 'bold',
                        textAlign: 'center',
                        verticalAlign: 'middle'
                      }}>
                        {timeSlot}
                      </td>
                      {[1, 2, 3, 4, 5, 6, 7].map(dayIndex => {
                        const schedule = scheduleGrid[timeIndex]?.[dayIndex];
                        return (
                          <td key={dayIndex} style={{ 
                            border: '1px solid #d9d9d9', 
                            padding: '8px', 
                            height: '100px', 
                            verticalAlign: 'top',
                            width: '120px'
                          }}>
                            {schedule && (
                              <div style={{
                                background: '#e6f7ff',
                                padding: '8px',
                                borderRadius: '6px',
                                fontSize: '12px',
                                lineHeight: '1.4',
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'center'
                              }}>
                                <div style={{ 
                                  fontWeight: 'bold', 
                                  color: '#1890ff',
                                  marginBottom: '4px',
                                  fontSize: '13px'
                                }}>
                                  {schedule.courseName}
                                </div>
                                <div style={{ color: '#666', marginBottom: '2px' }}>
                                  {schedule.teacher}
                                </div>
                                <div style={{ color: '#666' }}>
                                  {schedule.classroom}
                                </div>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <TableOutlined />
                列表视图
              </span>
            } 
            key="list"
          >
            <Table
              columns={columns}
              dataSource={filteredSchedules}
              rowKey="id"
              loading={loading}
              pagination={{
                total: filteredSchedules.length,
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ScheduleViewPage;

import React, { useState, useEffect, useMemo } from 'react';
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
} from 'antd';
import {
  CalendarOutlined,
  TableOutlined,
  PrinterOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { scheduleAPI } from '../../services/api';
import { normalizeSemester } from '../../utils/semester';
import ScheduleGrid, { type ScheduleItem as GridScheduleItem } from '../../components/education/ScheduleGrid';

const { Title } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

interface ScheduleListItem {
  id: number;
  course_code: string;
  course_name: string;
  teacher_name: string;
  classroom_name: string;
  time_slot_name: string;
  day_of_week: number;
  day_of_week_display: string;
  semester: string;
  status: string;
  status_display: string;
}

const ScheduleViewPage: React.FC = () => {
  const [schedules, setSchedules] = useState<ScheduleListItem[]>([]);
  const [selectedSemester, setSelectedSemester] = useState('2025-2026-1');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [currentWeek, setCurrentWeek] = useState(1);
  const [timeSlots, setTimeSlots] = useState<any[]>([]);
  const [scheduleTable, setScheduleTable] = useState<Record<number, Record<number, any>>>({});
  const [messageApi, contextHolder] = message.useMessage();

  // 获取真实的排课数据（列表 + 课程表）
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const sem = normalizeSemester(selectedSemester);
        const verbose = (import.meta as any).env?.VITE_VERBOSE_LOGS === 'true';

        const [listResp, tableResp] = await Promise.all([
          scheduleAPI.getSchedules({ semester: sem, week: String(currentWeek), page: currentPage, page_size: pageSize }),
          scheduleAPI.getScheduleTable({ semester: sem, week: String(currentWeek) })
        ]);

        if (verbose) {
          console.log('[ScheduleView] request params:', { sem, currentWeek, page: currentPage, pageSize });
        }

        if (listResp.data && listResp.data.results) {
          setSchedules(listResp.data.results || []);
        } else if (Array.isArray(listResp.data)) {
          setSchedules(listResp.data as any);
        }

        const tableData = tableResp?.data?.data ?? tableResp?.data;
        if (tableData) {
          setTimeSlots(tableData.time_slots || []);
          setScheduleTable(tableData.schedule_table || {});
          if (verbose) {
            const usedSlots = Object.values(tableData.schedule_table || {}).reduce((acc: Set<number>, day: any) => {
              Object.keys(day || {}).forEach((k) => day[k] && acc.add(Number(k)));
              return acc;
            }, new Set<number>());
            console.log('[ScheduleView] timeSlots:', (tableData.time_slots || []).length, 'usedSlots:', usedSlots.size);
          }
        } else if (verbose) {
          console.warn('[ScheduleView] tableResp has no data:', tableResp?.data);
        }
      } catch (error) {
        console.error('获取排课数据失败:', error);
        messageApi.error('获取排课数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedSemester, currentPage, pageSize, currentWeek]);

  const weekDays = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];

  const columns = [
    {
      title: '课程代码',
      dataIndex: 'course_code',
      key: 'course_code',
      width: 120,
    },
    {
      title: '课程名称',
      dataIndex: 'course_name',
      key: 'course_name',
      width: 150,
    },
    {
      title: '授课教师',
      dataIndex: 'teacher_name',
      key: 'teacher_name',
      width: 120,
    },
    {
      title: '教室',
      dataIndex: 'classroom_name',
      key: 'classroom_name',
      width: 100,
    },
    {
      title: '星期',
      dataIndex: 'day_of_week_display',
      key: 'day_of_week_display',
      width: 80,
    },
    {
      title: '时间段',
      dataIndex: 'time_slot_name',
      key: 'time_slot_name',
      width: 150,
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
    {
      title: '状态',
      dataIndex: 'status_display',
      key: 'status_display',
      width: 100,
      render: (statusDisplay: string) => (
        <Tag color={statusDisplay === '启用' ? 'green' : 'red'}>{statusDisplay}</Tag>
      ),
    },
  ];

  // 仅显示本周有课的时间段，避免表格过长
  const displayTimeSlots = useMemo(() => {
    const sortFn = (a: any, b: any) => {
      const ao = (a?.order ?? 0) - (b?.order ?? 0);
      if (ao !== 0) return ao;
      return String(a?.start_time || '').localeCompare(String(b?.start_time || ''));
    };
    if (!timeSlots?.length) return [] as any[];
    const used = new Set<number>();
    for (let day = 1; day <= 7; day++) {
      const daySlots = (scheduleTable as any)?.[day] || {};
      for (const tsId in daySlots) {
        if (daySlots[tsId]) used.add(Number(tsId));
      }
    }
    const filtered = timeSlots.filter(ts => used.has(ts.id));
    const base = filtered.length > 0 ? filtered : timeSlots;
    return [...base].sort(sortFn);
  }, [timeSlots, scheduleTable]);

  // 转换为 ScheduleGrid 数据结构
  const gridTimeSlots = useMemo(() => (
    (displayTimeSlots || []).map(ts => `${String(ts.start_time).slice(0, 5)}-${String(ts.end_time).slice(0, 5)}`)
  ), [displayTimeSlots]);

  const gridData: GridScheduleItem[] = useMemo(() => {
    const items: GridScheduleItem[] = [];
    for (let day = 1; day <= 7; day++) {
      const daySlots = (scheduleTable as any)?.[day] || {};
      for (const ts of displayTimeSlots || []) {
        const cell = daySlots?.[ts.id];
        if (cell) {
          items.push({
            id: `${cell.id || 's'}-${day}-${ts.id}`,
            course_id: Number(cell.id || 0),
            course_name: String(cell.course_name || ''),
            course_code: String(cell.course_code || ''),
            teacher_name: String(cell.teacher_name || ''),
            classroom: String(cell.classroom || ''),
            time_slot: String(ts.name || ''),
            day_of_week: day,
            start_time: String(ts.start_time || '').slice(0, 5),
            end_time: String(ts.end_time || '').slice(0, 5),
            week_range: String(cell.week_range || '')
          });
        }
      }
    }
    return items;
  }, [scheduleTable, displayTimeSlots]);
  const normalizedSelected = normalizeSemester(selectedSemester);
  const filteredSchedules = schedules.filter((s) => {
    const sem = String((s as any)?.semester || '');
    const normalized = normalizeSemester(sem);
    return sem === normalizedSelected || normalized === normalizedSelected;
  });

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
      messageApi.loading('正在生成Excel文件...', 0);

      // 调用后端API导出Excel
      const response = await scheduleAPI.exportSchedules({
        format: 'excel',
        semester: normalizeSemester(selectedSemester),
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

      messageApi.destroy();
      messageApi.success('Excel文件导出成功');
    } catch (error) {
      messageApi.destroy();
      console.error('导出Excel失败:', error);
      messageApi.error('导出Excel失败');
    }
  };

  const exportToPDF = async () => {
    try {
      messageApi.loading('正在生成PDF文件...', 0);

      // 调用后端API导出PDF
      const response = await scheduleAPI.exportSchedules({
        format: 'pdf',
        semester: normalizeSemester(selectedSemester),
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

      messageApi.destroy();
      messageApi.success('PDF文件导出成功');
    } catch (error) {
      messageApi.destroy();
      console.error('导出PDF失败:', error);
      messageApi.error('导出PDF失败');
    }
  };

  const exportToCSV = async () => {
    try {
      messageApi.loading('正在生成CSV文件...', 0);

      // 调用后端API导出CSV
      const response = await scheduleAPI.exportSchedules({
        format: 'csv',
        semester: normalizeSemester(selectedSemester),
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

      messageApi.destroy();
      messageApi.success('CSV文件导出成功');
    } catch (error) {
      messageApi.destroy();
      console.error('导出CSV失败:', error);
      messageApi.error('导出CSV失败');
    }
  };

  return (
    <div className="schedule-view-page">
      {contextHolder}
      <div className="page-header">
        <Title level={2}>课程表查看</Title>
        <p>查看当前学期的课程安排</p>
      </div>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16, position: 'relative', zIndex: 2 }}>
          <Col xs={24} sm={12} md={8}>
            <Select
              value={selectedSemester}
              onChange={(val) => { setSelectedSemester(val); setCurrentWeek(1); }}
              style={{ width: '100%' }}
              placeholder="选择学期"
              getPopupContainer={() => document.body}
              dropdownMatchSelectWidth={false}
              dropdownStyle={{ zIndex: 4000 }}
            >
              <Option value="2024春季">2024年春季学期</Option>
              <Option value="2025-2026-1">2025-2026学年第一学期</Option>
            </Select>
            <Select
              value={currentWeek}
              onChange={(v) => { setCurrentWeek(Number(v)); messageApi.success(`已切换到第${v}周`); }}
              style={{ width: '100%', marginTop: 8 }}
              placeholder="选择周次"
              getPopupContainer={() => document.body}
              dropdownMatchSelectWidth={false}
              dropdownStyle={{ zIndex: 4000 }}
            >
              {Array.from({ length: 20 }, (_, i) => (
                <Option key={i + 1} value={i + 1}>第{i + 1}周</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={16} style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={() => { const n = Math.max(1, currentWeek - 1); setCurrentWeek(n); messageApi.success(`已切换到第${n}周`); }} disabled={currentWeek <= 1}>上一周</Button>
              <Button onClick={() => { const n = Math.min(20, currentWeek + 1); setCurrentWeek(n); messageApi.success(`已切换到第${n}周`); }} disabled={currentWeek >= 20}>下一周</Button>
              <Tag color="blue">第{currentWeek}周</Tag>
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
            <ScheduleGrid
              scheduleData={gridData}
              timeSlots={gridTimeSlots}
              weekDays={weekDays.slice(1)}
              showWeekend={true}
            />
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
                current: currentPage,
                pageSize: pageSize,
                total: filteredSchedules.length,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
                onChange: (page, size) => {
                  setCurrentPage(page);
                  setPageSize(size || pageSize);
                },
              }}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ScheduleViewPage;

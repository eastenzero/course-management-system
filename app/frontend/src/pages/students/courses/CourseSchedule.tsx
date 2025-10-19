import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  Select,
  Button,
  Space,
  Typography,
  Tag,
  Empty,
  Spin,
  message,
  Row,
  Col
} from 'antd';
import {
  CalendarOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  UserOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import ScheduleGrid, { type ScheduleItem as GridScheduleItem } from '../../../components/education/ScheduleGrid';
import { studentAPI } from '../../../services/studentAPI';
import { normalizeSemester } from '../../../utils/semester';
import { scheduleAPI } from '../../../services/api';
import { useAppSelector } from '../../../store';

const { Option } = Select;
const { Title, Text } = Typography;

interface TimeSlot {
  id: number;
  name: string;
  start_time: string;
  end_time: string;
  order: number;
}

interface ScheduleItem {
  course_id: number;
  course_name: string;
  course_code: string;
  teacher_name: string;
  classroom: string;
  classroom_id: number;
  time_slot: string;
  time_slot_id: number;
  day_of_week: number;
  day_of_week_display: string;
  start_time: string;
  end_time: string;
  week_range: string;
  semester: string;
  grid_key: string;
}

const CourseSchedule: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('2024秋');
  const [currentWeek, setCurrentWeek] = useState<number>(1);
  const [exporting, setExporting] = useState(false);

  const MAX_WEEKS = 20;

  const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

  useEffect(() => {
    fetchTimeSlots();
  }, []);

  useEffect(() => {
    // 学生/教师需要 user.id 以附带筛选参数；管理员/未知类型不需要
    if (user?.user_type === 'student' || user?.user_type === 'teacher') {
      if (user?.id) fetchSchedule();
    } else {
      fetchSchedule();
    }
  }, [selectedSemester, currentWeek, user?.id, user?.user_type]);

  const fetchTimeSlots = async () => {
    try {
      const verbose = (import.meta as any).env?.VITE_VERBOSE_LOGS === 'true';
      // 优先使用 simple 接口，结构更稳定
      try {
        const simple = await scheduleAPI.getTimeSlotsSimple();
        const payload = simple.data?.data ?? simple.data;
        if (Array.isArray(payload)) {
          setTimeSlots(payload);
          if (verbose) console.log('[CourseSchedule] timeSlots(simple):', payload.length);
          return;
        }
      } catch (e) {
        if (verbose) console.warn('[CourseSchedule] simple timeslots not available, fallback.');
      }

      const response = await scheduleAPI.getTimeSlots();
      const payload = response.data?.data ?? response.data;
      if (Array.isArray(payload)) {
        setTimeSlots(payload);
      } else if (Array.isArray(payload?.results)) {
        setTimeSlots(payload.results);
      } else {
        setTimeSlots([]);
      }
    } catch (error: any) {
      console.error('获取时间段失败:', error);
      message.error('获取时间段失败');
      // 退回到硬编码时间段
      setTimeSlots([
        { id: 1, name: '第1节', start_time: '08:00', end_time: '09:40', order: 1 },
        { id: 2, name: '第2节', start_time: '10:00', end_time: '11:40', order: 2 },
        { id: 3, name: '第3节', start_time: '14:00', end_time: '15:40', order: 3 },
        { id: 4, name: '第4节', start_time: '16:00', end_time: '17:40', order: 4 },
        { id: 5, name: '第5节', start_time: '19:00', end_time: '20:40', order: 5 }
      ]);
    }
  };

  // 仅显示本周有课的时间段，并按顺序排序，避免表格过长与乱序
  const displayTimeSlots = useMemo(() => {
    const sortFn = (a: TimeSlot, b: TimeSlot) => {
      const ao = (a.order ?? 0) - (b.order ?? 0);
      if (ao !== 0) return ao;
      return String(a.start_time).localeCompare(String(b.start_time));
    };
    if (!timeSlots?.length) return [] as TimeSlot[];
    if (!schedule?.length) return [...timeSlots].sort(sortFn);
    const used = new Set<number>(schedule.map(s => s.time_slot_id));
    const filtered = timeSlots.filter(ts => used.has(ts.id));
    const base = filtered.length > 0 ? filtered : timeSlots;
    return [...base].sort(sortFn);
  }, [timeSlots, schedule]);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const params: any = {};
      // 仅在用户角色匹配时传递筛选参数
      if (user?.user_type === 'student') {
        params.user_type = 'student';
        params.user_id = user.id;
      } else if (user?.user_type === 'teacher') {
        params.user_type = 'teacher';
        params.user_id = user.id;
      }
      // 始终传递规范化的学期，防止后端 400（缺少学期参数）
      const semParam = selectedSemester ? normalizeSemester(selectedSemester) : normalizeSemester('2024-1');
      params.semester = semParam;
      params.week = String(currentWeek);
      
      const verbose = (import.meta as any).env?.VITE_VERBOSE_LOGS === 'true';
      if (verbose) {
        console.log('[CourseSchedule] fetch params:', params);
      }

      let response = await studentAPI.getSchedule(params);

      // 兼容后端返回包装或直接返回
      let payload = response?.data?.data ?? response?.data;

      // 如果拿不到schedule_table，尝试直接调用 scheduleAPI 作为后备
      if (!payload?.schedule_table) {
        if (verbose) console.warn('[CourseSchedule] primary resp missing schedule_table, trying fallback ...');
        const fb = await scheduleAPI.getScheduleTable(params);
        payload = fb?.data?.data ?? fb?.data;
      }
      
      // 转换后端数据格式为前端需要的格式
      if (payload?.schedule_table) {
        const scheduleTable = payload.schedule_table;
        const timeSlotsData = payload.time_slots || timeSlots;
        
        // 将表格数据转换为课程列表
        const scheduleItems: ScheduleItem[] = [];
        
        // 遍历每一天（1-7表示周一到周日）
        for (let day = 1; day <= 7; day++) {
          const daySchedule = scheduleTable[day];
          if (daySchedule) {
            // 遍历每个时间段
            for (const timeSlotId in daySchedule) {
              const courseData = daySchedule[timeSlotId];
              if (courseData) {
                const timeSlot = timeSlotsData.find((ts: any) => ts.id === parseInt(timeSlotId));
                
                scheduleItems.push({
                  course_id: courseData.id,
                  course_name: courseData.course_name,
                  course_code: courseData.course_code,
                  teacher_name: courseData.teacher_name,
                  classroom: courseData.classroom,
                  classroom_id: 0, // 默认值，后端没有返回这个字段
                  time_slot: timeSlot?.name || `第${timeSlotId}节`,
                  time_slot_id: parseInt(timeSlotId),
                  day_of_week: day,
                  day_of_week_display: weekDays[day - 1],
                  start_time: timeSlot?.start_time || '',
                  end_time: timeSlot?.end_time || '',
                  week_range: courseData.week_range,
                  semester: semParam,
                  grid_key: `${day}-${timeSlotId}`
                });
              }
            }
          }
        }
        
        if (verbose) {
          console.log('[CourseSchedule] parsed items:', scheduleItems.length);
        }
        setSchedule(scheduleItems);
      } else {
        // 如果已经是数组格式，直接使用
        if (Array.isArray(payload)) {
          setSchedule(payload);
        } else {
          if (verbose) console.warn('[CourseSchedule] no schedule_table and payload not array:', payload);
          setSchedule([]);
        }
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || '获取课程表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExportSchedule = async () => {
    try {
      setExporting(true);
      const params: any = {
        semester: selectedSemester ? normalizeSemester(selectedSemester) : normalizeSemester('2024-1'),
        format: 'excel'
      };
      
      const response = await studentAPI.exportSchedule(params);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `课程表_${selectedSemester || '全部'}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('课程表导出成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '导出课程表失败');
    } finally {
      setExporting(false);
    }
  };

  // 供 ScheduleGrid 使用的数据
  const gridTimeSlots = useMemo(() => (
    (displayTimeSlots || []).map(ts => `${ts.start_time}-${ts.end_time}`)
  ), [displayTimeSlots]);

  const gridData: GridScheduleItem[] = useMemo(() => (
    (schedule || []).map((s, idx) => ({
      id: `${s.course_id}-${s.day_of_week}-${s.time_slot_id}-${idx}`,
      course_id: s.course_id,
      course_name: s.course_name,
      course_code: s.course_code,
      teacher_name: s.teacher_name,
      classroom: s.classroom,
      time_slot: s.time_slot,
      day_of_week: s.day_of_week,
      start_time: s.start_time,
      end_time: s.end_time,
      week_range: s.week_range
    }))
  ), [schedule]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ width: 200, height: 80 }} />
        </Spin>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', position: 'relative', zIndex: 1 }}>
        <Title level={2}>课程表</Title>
        <Space>
          <Select
            placeholder="选择学期"
            style={{ width: 200 }}
            value={selectedSemester}
            onChange={(val) => { setSelectedSemester(val); setCurrentWeek(1); }}
            getPopupContainer={() => document.body}
            dropdownMatchSelectWidth={false}
            dropdownStyle={{ zIndex: 4000 }}
          >
            <Option value="2024春">2024春季学期</Option>
            <Option value="2024秋">2024秋季学期</Option>
            <Option value="2025春">2025春季学期</Option>
          </Select>
          <Select
            placeholder="选择周次"
            style={{ width: 120 }}
            value={currentWeek}
            onChange={(w) => { setCurrentWeek(Number(w)); message.success(`已切换到第${w}周`); }}
            getPopupContainer={() => document.body}
            dropdownMatchSelectWidth={false}
            dropdownStyle={{ zIndex: 4000 }}
          >
            {Array.from({ length: MAX_WEEKS }, (_, i) => (
              <Option key={i + 1} value={i + 1}>第{i + 1}周</Option>
            ))}
          </Select>
          <Button
            disabled={currentWeek <= 1}
            onClick={() => setCurrentWeek((w) => { const n = Math.max(1, w - 1); message.success(`已切换到第${n}周`); return n; })}
          >
            上一周
          </Button>
          <Button
            disabled={currentWeek >= MAX_WEEKS}
            onClick={() => setCurrentWeek((w) => { const n = Math.min(MAX_WEEKS, w + 1); message.success(`已切换到第${n}周`); return n; })}
          >
            下一周
          </Button>
          <Tag color="blue">第{currentWeek}周</Tag>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={handleExportSchedule}
          >
            导出课程表
          </Button>
        </Space>
      </div>

      {schedule.length === 0 ? (
        <Card>
          <Empty description="暂无课程安排" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        </Card>
      ) : (
        <>
          <ScheduleGrid
            scheduleData={gridData}
            timeSlots={gridTimeSlots}
            weekDays={weekDays}
            showWeekend={true}
          />

          <div style={{ marginTop: '24px' }}>
            <Title level={4}>课程列表</Title>
            <Row gutter={[16, 16]}>
              {schedule.map((course, index) => (
                <Col xs={24} sm={12} lg={8} key={index}>
                  <Card size="small">
                    <div style={{ marginBottom: '8px' }}>
                      <Text strong>{course.course_name}</Text>
                      <Tag style={{ marginLeft: '8px' }}>{course.course_code}</Tag>
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      <div style={{ marginBottom: '4px' }}>
                        <CalendarOutlined /> {weekDays[course.day_of_week - 1]}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <ClockCircleOutlined /> {course.start_time}-{course.end_time}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <EnvironmentOutlined /> {course.classroom}
                      </div>
                      <div style={{ marginBottom: '4px' }}>
                        <UserOutlined /> {course.teacher_name}
                      </div>
                      <div>
                        周次：{course.week_range}
                      </div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </>
      )}
    </div>
  );
};

export default CourseSchedule;

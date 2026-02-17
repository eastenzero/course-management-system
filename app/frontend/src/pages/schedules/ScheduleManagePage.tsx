import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Table,
  Button,
  Space,
  Select,
  Modal,
  Form,
  Input,
  message,
  Row,
  Col,
  Tag,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { scheduleAPI, courseAPI, userAPI, classroomAPI } from '../../services/api';
import { normalizeSemester, semesterToAcademicYear } from '../../utils/semester';
import ScheduleImportExport from '../../components/education/ScheduleImportExport';

const { Title } = Typography;
const { Option } = Select;

interface Schedule {
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

const ScheduleManagePage: React.FC = () => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [selectedSemester, setSelectedSemester] = useState('2025-2026-1');
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [courseOptions, setCourseOptions] = useState<any[]>([]);
  const [teacherOptions, setTeacherOptions] = useState<any[]>([]);
  const [classroomOptions, setClassroomOptions] = useState<any[]>([]);
  const [timeSlotOptions, setTimeSlotOptions] = useState<any[]>([]);
  const [exportVisible, setExportVisible] = useState(false);

  // 获取课程表数据
  const fetchSchedules = async (page = 1, pageSize = 20, semester = '') => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (semester) {
        params.semester = normalizeSemester(semester);
      }

      const response = await scheduleAPI.getSchedules(params);

      if (response.data && response.data.results) {
        setSchedules(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      } else {
        const items = response.data?.data || response.data || [];
        const list = Array.isArray(items) ? items : [];
        setSchedules(list);
        setPagination({
          current: page,
          pageSize,
          total: list.length,
        });
      }
    } catch (error) {
      console.error('获取课程表失败:', error);
      message.error('获取课程表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules(1, 20, selectedSemester);
  }, [selectedSemester]);

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const [coursesResp, teachersResp, classroomsResp, timeSlotsResp] = await Promise.all([
          courseAPI.getCourses({ page_size: 1000 }),
          userAPI.getUsers({ user_type: 'teacher', page_size: 1000 }),
          classroomAPI.getClassrooms({ page_size: 1000 }),
          scheduleAPI.getTimeSlotsSimple()
        ]);

        const courses = coursesResp.data?.results || coursesResp.data?.data || [];
        const teachers = teachersResp.data?.results || teachersResp.data?.data || [];
        const classrooms = classroomsResp.data?.results || classroomsResp.data?.data || [];
        const timeSlots = timeSlotsResp.data?.data || timeSlotsResp.data?.results || [];

        setCourseOptions(courses);
        setTeacherOptions(teachers);
        setClassroomOptions(classrooms);
        setTimeSlotOptions(timeSlots);
      } catch (e) {
        // ignore
      }
    };
    loadOptions();
  }, []);

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
    {
      title: '状态',
      dataIndex: 'status_display',
      key: 'status_display',
      width: 80,
      render: (statusDisplay: string, record: Schedule) => (
        <Tag color={record.status === 'active' ? 'green' : 'red'}>
          {statusDisplay}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (record: Schedule) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个课程安排吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleAdd = () => {
    setEditingSchedule(null);
    form.resetFields();
    form.setFieldsValue({ semester: selectedSemester });
    setIsModalVisible(true);
  };

  const handleEdit = async (schedule: Schedule) => {
    try {
      setEditingSchedule(schedule);
      setIsModalVisible(true);
      const detail = await scheduleAPI.getSchedule(schedule.id);
      const data = detail.data?.data || detail.data;
      if (data) {
        form.setFieldsValue({
          course: data.course,
          teacher: data.teacher,
          classroom: data.classroom,
          day_of_week: data.day_of_week,
          time_slot: data.time_slot,
          week_range: data.week_range,
          semester: data.semester,
        });
      }
    } catch (e) {
      // ignore
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await scheduleAPI.deleteSchedule(id);
      message.success('课程安排删除成功');
      // 重新获取当前页数据
      fetchSchedules(pagination.current, pagination.pageSize, selectedSemester);
    } catch (error) {
      console.error('删除课程安排失败:', error);
      message.error('删除课程安排失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      const sem = normalizeSemester(values.semester);
      const payload = {
        course: values.course,
        teacher: values.teacher,
        classroom: values.classroom,
        time_slot: values.time_slot,
        day_of_week: values.day_of_week,
        week_range: values.week_range,
        semester: sem,
        academic_year: semesterToAcademicYear(sem),
        notes: values.notes,
      };

      const conflictResp = await scheduleAPI.checkConflicts({
        course_id: payload.course,
        teacher_id: payload.teacher,
        classroom_id: payload.classroom,
        day_of_week: payload.day_of_week,
        time_slot_id: payload.time_slot,
        semester: payload.semester,
        exclude_schedule_id: editingSchedule?.id,
      });
      const hasConflicts = conflictResp.data?.data?.has_conflicts === true;
      if (hasConflicts) {
        message.error('时间冲突，请调整后再试');
        return;
      }

      if (editingSchedule) {
        await scheduleAPI.updateSchedule(editingSchedule.id, payload);
        message.success('课程安排更新成功');
      } else {
        await scheduleAPI.createSchedule(payload);
        message.success('课程安排添加成功');
      }

      setIsModalVisible(false);
      form.resetFields();
      fetchSchedules(pagination.current, pagination.pageSize, selectedSemester);
    } catch (error) {
      console.error('提交失败:', error);
      message.error('提交失败');
    }
  };



  return (
    <div className="schedule-manage-page">
      <div className="page-header">
        <Title level={2}>排课管理</Title>
        <p>管理课程时间安排，支持冲突检测</p>
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
              <Option value="2024春季">2024年春季学期</Option>
              <Option value="2025-2026-1">2025-2026学年第一学期</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={16} style={{ textAlign: 'right' }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              添加课程安排
            </Button>
            <Button
              style={{ marginLeft: 8 }}
              icon={<DownloadOutlined />}
              onClick={() => setExportVisible(true)}
            >
              导出课程表
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={schedules}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              fetchSchedules(page, pageSize, selectedSemester);
            },
            onShowSizeChange: (_current, size) => {
              fetchSchedules(1, size, selectedSemester);
            },
          }}
        />
      </Card>

      <Modal
        title={editingSchedule ? '编辑课程安排' : '添加课程安排'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={() => setIsModalVisible(false)}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ semester: selectedSemester }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="course"
                label="课程"
                rules={[{ required: true, message: '请选择课程' }]}
              >
                <Select placeholder="选择课程" showSearch optionFilterProp="label">
                  {courseOptions.map((c: any) => (
                    <Option key={c.id} value={c.id} label={`${c.code || ''} ${c.name || ''}`}>{`${c.code || ''} ${c.name || ''}`}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="teacher"
                label="授课教师"
                rules={[{ required: true, message: '请选择授课教师' }]}
              >
                <Select placeholder="选择教师" showSearch optionFilterProp="label">
                  {teacherOptions.map((t: any) => {
                    const name = `${t.first_name || ''} ${t.last_name || ''}`.trim() || t.username;
                    return (
                      <Option key={t.id} value={t.id} label={name}>{name}</Option>
                    );
                  })}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="classroom"
                label="教室"
                rules={[{ required: true, message: '请选择教室' }]}
              >
                <Select placeholder="选择教室" showSearch optionFilterProp="label">
                  {classroomOptions.map((r: any) => (
                    <Option key={r.id} value={r.id} label={r.full_name || r.room_number}>{r.full_name || r.room_number}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="day_of_week"
                label="星期"
                rules={[{ required: true, message: '请选择星期' }]}
              >
                <Select placeholder="选择星期">
                  {weekDays.slice(1).map((day, index) => (
                    <Option key={index + 1} value={index + 1}>{day}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="time_slot"
                label="上课时间"
                rules={[{ required: true, message: '请选择时间段' }]}
              >
                <Select placeholder="选择时间段" showSearch optionFilterProp="label">
                  {timeSlotOptions.map((ts: any) => (
                    <Option key={ts.id} value={ts.id} label={`${ts.name || ''} (${ts.start_time}-${ts.end_time})`}>
                      {`${ts.name || ''} (${ts.start_time}-${ts.end_time})`}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="week_range"
                label="周次"
                rules={[{ required: true, message: '请输入周次' }]}
              >
                <Input placeholder="如：1-16" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="semester"
                label="学期"
                rules={[{ required: true, message: '请选择学期' }]}
              >
                <Select placeholder="选择学期">
                  <Option value="2024春季">2024年春季学期</Option>
                  <Option value="2025-2026-1">2025-2026学年第一学期</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      <ScheduleImportExport
        visible={exportVisible}
        onCancel={() => setExportVisible(false)}
        mode="export"
        semester={selectedSemester}
        onExportRequest={async (opts: any) => {
          const sem = normalizeSemester(opts.semester || selectedSemester);
          const format = opts.format === 'csv' ? 'csv' : 'excel';
          const params = {
            semester: sem,
            format,
            include_weekend: !!opts.includeWeekend,
            group_by: opts.groupBy || 'teacher',
          } as any;
          const resp = await scheduleAPI.exportSchedules(params);
          const mime = format === 'csv'
            ? 'text/csv;charset=utf-8;'
            : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          const blob = new Blob([resp.data], { type: mime });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `课程表_${sem}.${format === 'csv' ? 'csv' : 'xlsx'}`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          setExportVisible(false);
        }}
      />
    </div>
  );
};

export default ScheduleManagePage;

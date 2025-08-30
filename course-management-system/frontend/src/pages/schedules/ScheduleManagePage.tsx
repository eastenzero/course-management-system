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
  TimePicker,
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
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { scheduleAPI } from '../../services/api';

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
  const [selectedSemester, setSelectedSemester] = useState('2024-spring');
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 获取课程表数据
  const fetchSchedules = async (page = 1, pageSize = 20, semester = '') => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (semester) {
        params.semester = semester;
      }

      const response = await scheduleAPI.getSchedules(params);

      if (response.data && response.data.results) {
        setSchedules(response.data.results.data || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
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

  const handleEdit = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    form.setFieldsValue({
      ...schedule,
      time: [dayjs(schedule.startTime, 'HH:mm'), dayjs(schedule.endTime, 'HH:mm')],
    });
    setIsModalVisible(true);
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
      const [startTime, endTime] = values.time;

      // 检查时间冲突
      const conflictCheck = checkTimeConflict(values, editingSchedule?.id);
      if (conflictCheck.hasConflict) {
        message.error(`时间冲突：${conflictCheck.message}`);
        return;
      }

      const scheduleData = {
        ...values,
        startTime: startTime.format('HH:mm'),
        endTime: endTime.format('HH:mm'),
      };

      if (editingSchedule) {
        setSchedules(schedules.map(schedule =>
          schedule.id === editingSchedule.id
            ? { ...schedule, ...scheduleData }
            : schedule
        ));
        message.success('课程安排更新成功');
      } else {
        const newSchedule: Schedule = {
          id: Date.now().toString(),
          ...scheduleData,
        };
        setSchedules([...schedules, newSchedule]);
        message.success('课程安排添加成功');
      }

      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 检查时间冲突
  const checkTimeConflict = (newSchedule: any, excludeId?: string) => {
    const conflicts = schedules.filter(schedule => {
      if (excludeId && schedule.id === excludeId) return false;
      
      return (
        schedule.semester === newSchedule.semester &&
        schedule.dayOfWeek === newSchedule.dayOfWeek &&
        (
          schedule.classroom === newSchedule.classroom ||
          schedule.teacher === newSchedule.teacher
        )
      );
    });

    if (conflicts.length > 0) {
      const conflict = conflicts[0];
      const conflictType = conflict.classroom === newSchedule.classroom ? '教室' : '教师';
      return {
        hasConflict: true,
        message: `${conflictType}在该时间段已有安排（${conflict.courseName}）`
      };
    }

    return { hasConflict: false, message: '' };
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
              <Option value="2024-spring">2024年春季学期</Option>
              <Option value="2024-fall">2024年秋季学期</Option>
              <Option value="2025-spring">2025年春季学期</Option>
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
            onShowSizeChange: (current, size) => {
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
                name="courseCode"
                label="课程代码"
                rules={[{ required: true, message: '请输入课程代码' }]}
              >
                <Input placeholder="如：CS101" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="courseName"
                label="课程名称"
                rules={[{ required: true, message: '请输入课程名称' }]}
              >
                <Input placeholder="如：数据结构" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="teacher"
                label="授课教师"
                rules={[{ required: true, message: '请输入授课教师' }]}
              >
                <Input placeholder="如：张教授" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="classroom"
                label="教室"
                rules={[{ required: true, message: '请输入教室' }]}
              >
                <Input placeholder="如：A101" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="dayOfWeek"
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
            <Col span={16}>
              <Form.Item
                name="time"
                label="上课时间"
                rules={[{ required: true, message: '请选择上课时间' }]}
              >
                <TimePicker.RangePicker
                  format="HH:mm"
                  placeholder={['开始时间', '结束时间']}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="weeks"
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
                  <Option value="2024-1">2024年春季学期</Option>
                  <Option value="2024-2">2024年秋季学期</Option>
                  <Option value="2025-1">2025年春季学期</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default ScheduleManagePage;

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Form,
  Input,
  Select,
  Button,
  Row,
  Col,
  message,
  Space,
  Spin,
  InputNumber,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { courseAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

interface Course {
  id: number;
  name: string;
  code: string;
  credits: number;
  department: string;
  course_type: string;
  course_type_display: string;
  max_students: number;
  current_enrollment: number;
  hours: number;
  semester: string;
  academic_year: string;
  is_active: boolean;
  is_published: boolean;
  description?: string;
}

interface CourseFormData {
  code: string;
  name: string;
  credits: number;
  department: string;
  course_type: string;
  max_students: number;
  hours: number;
  semester: string;
  academic_year: string;
  description?: string;
}

const CourseEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchCourseDetail = async () => {
      try {
        setLoading(true);

        if (!id) {
          message.error('课程ID不存在');
          navigate('/courses/list');
          return;
        }

        const response = await courseAPI.getCourse(parseInt(id));
        const courseData = response.data;

        setCourse(courseData);
        form.setFieldsValue({
          code: courseData.code,
          name: courseData.name,
          credits: courseData.credits,
          department: courseData.department,
          course_type: courseData.course_type,
          max_students: courseData.max_students,
          hours: courseData.hours,
          semester: courseData.semester,
          academic_year: courseData.academic_year,
          description: courseData.description,
        });
      } catch (error) {
        console.error('获取课程详情失败:', error);
        message.error('获取课程详情失败');
        navigate('/courses/list');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCourseDetail();
    }
  }, [id, form, navigate]);

  const handleSubmit = async (values: CourseFormData) => {
    try {
      setSubmitting(true);

      if (!id) {
        message.error('课程ID不存在');
        return;
      }

      await courseAPI.updateCourse(parseInt(id), values);

      message.success('课程更新成功');
      navigate(`/courses/${id}`);
    } catch (error) {
      console.error('更新课程失败:', error);
      message.error('更新失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate(`/courses/${id}`);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ minHeight: '200px' }} />
        </Spin>
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>课程不存在</Title>
        <Button onClick={() => navigate('/courses/list')}>
          返回课程列表
        </Button>
      </div>
    );
  }

  return (
    <div className="course-edit-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleCancel}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>编辑课程</Title>
        </Space>
        <p>修改课程信息</p>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="code"
                label="课程代码"
                rules={[
                  { required: true, message: '请输入课程代码' },
                  { pattern: /^[A-Z]{2,4}\d{3}$/, message: '格式：2-4个大写字母+3位数字，如CS101' }
                ]}
              >
                <Input placeholder="如：CS101" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="课程名称"
                rules={[
                  { required: true, message: '请输入课程名称' },
                  { min: 2, max: 50, message: '课程名称长度为2-50个字符' }
                ]}
              >
                <Input placeholder="如：数据结构" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="credits"
                label="学分"
                rules={[{ required: true, message: '请选择学分' }]}
              >
                <Select>
                  <Option value={1}>1学分</Option>
                  <Option value={2}>2学分</Option>
                  <Option value={3}>3学分</Option>
                  <Option value={4}>4学分</Option>
                  <Option value={5}>5学分</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="department"
                label="院系"
                rules={[{ required: true, message: '请选择院系' }]}
              >
                <Select placeholder="选择院系">
                  <Option value="计算机系">计算机系</Option>
                  <Option value="数学系">数学系</Option>
                  <Option value="外语系">外语系</Option>
                  <Option value="物理系">物理系</Option>
                  <Option value="化学系">化学系</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="capacity"
                label="课程容量"
                rules={[
                  { required: true, message: '请输入课程容量' },
                  { type: 'number', min: 1, max: 500, message: '容量范围：1-500人' }
                ]}
              >
                <Input 
                  type="number" 
                  placeholder="如：120"
                  disabled={course.enrolled > 0} // 如果已有学生选课，不允许修改容量
                />
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
                name="status"
                label="课程状态"
                rules={[{ required: true, message: '请选择状态' }]}
              >
                <Select>
                  <Option value="active">开放选课</Option>
                  <Option value="inactive">暂停选课</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="课程描述"
            rules={[{ max: 500, message: '描述不能超过500个字符' }]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder="请输入课程简介、教学目标、主要内容等..." 
            />
          </Form.Item>

          {course.enrolled > 0 && (
            <div style={{ 
              background: '#fff7e6', 
              border: '1px solid #ffd591', 
              borderRadius: '6px', 
              padding: '12px', 
              marginBottom: '16px' 
            }}>
              <strong>注意：</strong>该课程已有 {course.enrolled} 名学生选课，修改某些信息可能会影响学生的选课状态。
            </div>
          )}

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={submitting}
                icon={<SaveOutlined />}
              >
                保存修改
              </Button>
              <Button onClick={handleCancel}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CourseEditPage;

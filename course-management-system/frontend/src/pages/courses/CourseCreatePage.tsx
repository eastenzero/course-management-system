import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  InputNumber,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { courseAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

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

const CourseCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: CourseFormData) => {
    try {
      setLoading(true);

      // 调用API创建课程
      const response = await courseAPI.createCourse({
        ...values,
        is_active: true,
        is_published: true,
      });

      message.success('课程创建成功');
      navigate('/courses/list');
    } catch (error) {
      console.error('创建课程失败:', error);
      message.error('创建失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/courses/list');
  };

  return (
    <div className="course-create-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleCancel}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>创建课程</Title>
        </Space>
        <p>填写课程基本信息</p>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            credits: 3,
            max_students: 100,
            hours: 48,
            course_type: 'required',
            semester: 'spring',
            academic_year: '2024'
          }}
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
                rules={[{ required: true, message: '请输入院系' }]}
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
                name="course_type"
                label="课程类型"
                rules={[{ required: true, message: '请选择课程类型' }]}
              >
                <Select>
                  <Option value="required">必修课</Option>
                  <Option value="elective">选修课</Option>
                  <Option value="public">公共课</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="max_students"
                label="最大学生数"
                rules={[
                  { required: true, message: '请输入最大学生数' },
                  { type: 'number', min: 1, max: 500, message: '容量范围：1-500人' }
                ]}
              >
                <InputNumber min={1} max={500} placeholder="120" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="hours"
                label="总学时"
                rules={[
                  { required: true, message: '请输入总学时' },
                  { type: 'number', min: 1, max: 200, message: '学时范围：1-200' }
                ]}
              >
                <InputNumber min={1} max={200} placeholder="48" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="semester"
                label="学期"
                rules={[{ required: true, message: '请选择学期' }]}
              >
                <Select>
                  <Option value="spring">春季学期</Option>
                  <Option value="fall">秋季学期</Option>
                  <Option value="summer">夏季学期</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="academic_year"
                label="学年"
                rules={[{ required: true, message: '请输入学年' }]}
              >
                <Select>
                  <Option value="2024">2024年</Option>
                  <Option value="2025">2025年</Option>
                  <Option value="2026">2026年</Option>
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

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                创建课程
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

export default CourseCreatePage;

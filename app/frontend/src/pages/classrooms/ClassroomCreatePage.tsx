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
  Checkbox,
  Switch,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { classroomAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface ClassroomFormData {
  name: string;
  building: number;
  room_number: string;
  floor: number;
  capacity: number;
  room_type: 'lecture' | 'lab' | 'seminar' | 'computer' | 'multimedia';
  equipment: string[];
  is_available: boolean;
  description?: string;
}

const ClassroomCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const equipmentOptions = [
    { label: '投影仪', value: '投影仪' },
    { label: '音响', value: '音响' },
    { label: '黑板', value: '黑板' },
    { label: '白板', value: '白板' },
    { label: '电脑', value: '电脑' },
    { label: '空调', value: '空调' },
    { label: '实验台', value: '实验台' },
    { label: '通风设备', value: '通风设备' },
    { label: '安全设备', value: '安全设备' },
    { label: '多媒体设备', value: '多媒体设备' },
    { label: '圆桌', value: '圆桌' },
    { label: '讲台', value: '讲台' },
  ];

  const typeOptions = [
    { value: 'lecture', label: '阶梯教室' },
    { value: 'lab', label: '实验室' },
    { value: 'seminar', label: '研讨室' },
    { value: 'computer', label: '机房' },
    { value: 'multimedia', label: '多媒体教室' },
  ];

  const buildingOptions = [
    { value: 1, label: 'A栋' },
    { value: 2, label: 'B栋' },
    { value: 3, label: 'C栋' },
    { value: 4, label: 'D栋' },
    { value: 5, label: 'E栋' },
  ];

  const handleSubmit = async (values: ClassroomFormData) => {
    try {
      setLoading(true);

      // 调用API创建教室
      await classroomAPI.createClassroom({
        ...values,
        is_active: true,
      });

      message.success('教室创建成功');
      navigate('/classrooms/list');
    } catch (error) {
      console.error('创建教室失败:', error);
      message.error('创建失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/classrooms/list');
  };

  return (
    <div className="classroom-create-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={handleCancel}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>创建教室</Title>
        </Space>
        <p>填写教室基本信息和设备配置</p>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            is_available: true,
            capacity: 50,
            floor: 1,
            equipment: [],
            building: 1
          }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="name"
                label="教室名称"
                rules={[
                  { required: true, message: '请输入教室名称' },
                  { pattern: /^[A-Z]\d{3}$/, message: '格式：1个大写字母+3位数字，如A101' }
                ]}
              >
                <Input placeholder="如：A101" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="room_number"
                label="房间号"
                rules={[
                  { required: true, message: '请输入房间号' },
                  { pattern: /^\d{3}$/, message: '格式：3位数字，如101' }
                ]}
              >
                <Input placeholder="如：101" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="building"
                label="所在楼栋"
                rules={[{ required: true, message: '请选择楼栋' }]}
              >
                <Select placeholder="选择楼栋">
                  {buildingOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="floor"
                label="楼层"
                rules={[
                  { required: true, message: '请输入楼层' },
                  { type: 'number', min: 1, max: 20, message: '楼层范围：1-20' }
                ]}
              >
                <InputNumber
                  placeholder="楼层"
                  style={{ width: '100%' }}
                  min={1}
                  max={20}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="room_type"
                label="教室类型"
                rules={[{ required: true, message: '请选择教室类型' }]}
              >
                <Select placeholder="选择教室类型">
                  {typeOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="capacity"
                label="容量（人）"
                rules={[
                  { required: true, message: '请输入教室容量' },
                  { type: 'number', min: 1, max: 500, message: '容量范围：1-500人' }
                ]}
              >
                <InputNumber 
                  placeholder="教室容量" 
                  style={{ width: '100%' }}
                  min={1}
                  max={500}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="is_available"
                label="是否可用"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="可用" 
                  unCheckedChildren="不可用" 
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="equipment"
            label="设备配置"
            rules={[{ required: true, message: '请选择至少一项设备' }]}
          >
            <Checkbox.Group>
              <Row gutter={[16, 8]}>
                {equipmentOptions.map(option => (
                  <Col span={6} key={option.value}>
                    <Checkbox value={option.value}>
                      {option.label}
                    </Checkbox>
                  </Col>
                ))}
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="description"
            label="教室描述"
            rules={[{ max: 500, message: '描述不能超过500个字符' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="请输入教室的详细描述、特殊用途、注意事项等..." 
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
                创建教室
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

export default ClassroomCreatePage;

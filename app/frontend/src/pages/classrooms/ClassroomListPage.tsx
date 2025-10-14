import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Table,
  Button,
  Space,
  Card,
  Input,
  Select,
  Tag,
  message,
  Popconfirm,
  Row,
  Col,
  Badge,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  EyeOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { classroomAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

interface Classroom {
  id: number;
  name: string;
  full_name: string;
  building: number;
  building_name: string;
  building_code: string;
  room_number: string;
  floor: number;
  capacity: number;
  room_type: string;
  room_type_display: string;
  is_available: boolean;
  is_active: boolean;
}

const ClassroomListPage: React.FC = () => {
  const navigate = useNavigate();
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedBuilding, setSelectedBuilding] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 获取教室数据
  const fetchClassrooms = async (page = 1, pageSize = 20, search = '', building = '', type = '') => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: pageSize,
      };

      if (search) {
        params.search = search;
      }

      if (building) {
        params.building_name = building;
      }

      if (type) {
        params.room_type = type;
      }

      const response = await classroomAPI.getClassrooms(params);

      if (response.data && response.data.results) {
        setClassrooms(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      console.error('获取教室列表失败:', error);
      message.error('获取教室列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClassrooms();
  }, []);

  // 搜索处理
  const handleSearch = () => {
    fetchClassrooms(1, pagination.pageSize, searchText, selectedBuilding, selectedType);
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setSelectedBuilding('');
    setSelectedType('');
    fetchClassrooms(1, pagination.pageSize);
  };

  const getTypeColor = (type: string): string => {
    const colorMap = {
      lecture: 'blue',
      lab: 'green',
      seminar: 'orange',
      computer: 'purple',
      multimedia: 'cyan',
    };
    return colorMap[type as keyof typeof colorMap] || 'default';
  };

  const columns = [
    {
      title: '教室名称',
      dataIndex: 'full_name',
      key: 'full_name',
      width: 150,
      render: (fullName: string, record: Classroom) => (
        <Space>
          <HomeOutlined />
          <span>{fullName}</span>
        </Space>
      ),
    },
    {
      title: '楼栋',
      dataIndex: 'building_name',
      key: 'building_name',
      width: 100,
    },
    {
      title: '房间号',
      dataIndex: 'room_number',
      key: 'room_number',
      width: 100,
    },
    {
      title: '楼层',
      dataIndex: 'floor',
      key: 'floor',
      width: 80,
      render: (floor: number) => `${floor}楼`,
    },
    {
      title: '容量',
      dataIndex: 'capacity',
      key: 'capacity',
      width: 80,
      align: 'center' as const,
      render: (capacity: number) => `${capacity}人`,
    },
    {
      title: '类型',
      dataIndex: 'room_type_display',
      key: 'room_type',
      width: 120,
      render: (typeDisplay: string, record: Classroom) => (
        <Tag color={getTypeColor(record.room_type)}>
          {typeDisplay}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_available',
      key: 'is_available',
      width: 100,
      render: (isAvailable: boolean) => (
        <Badge
          status={isAvailable ? 'success' : 'error'}
          text={isAvailable ? '可用' : '不可用'}
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (record: Classroom) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/classrooms/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/classrooms/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个教室吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleDelete = async (id: number) => {
    try {
      await classroomAPI.deleteClassroom(id);
      message.success('教室删除成功');
      // 重新获取当前页数据
      fetchClassrooms(pagination.current, pagination.pageSize, searchText, selectedBuilding, selectedType);
    } catch (error) {
      console.error('删除教室失败:', error);
      message.error('删除教室失败');
    }
  };

  // 获取楼栋和类型列表用于筛选
  const buildings = Array.from(new Set(classrooms.map(classroom => classroom.building_name).filter(Boolean)));
  const classroomTypes = Array.from(new Set(classrooms.map(classroom => classroom.room_type).filter(Boolean)));
  const types = classroomTypes.map(type => ({
    value: type,
    label: classrooms.find(c => c.room_type === type)?.room_type_display || type
  }));

  return (
    <div className="classroom-list-page">
      <div className="page-header">
        <Title level={2}>教室管理</Title>
        <p>管理教室信息、设备和使用状态</p>
      </div>

      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8} md={6}>
            <Input
              placeholder="搜索教室名称或楼栋"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
            />
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="选择楼栋"
              style={{ width: '100%' }}
              value={selectedBuilding}
              onChange={setSelectedBuilding}
              allowClear
            >
              {buildings.map(building => (
                <Option key={building} value={building}>{building}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="选择类型"
              style={{ width: '100%' }}
              value={selectedType}
              onChange={setSelectedType}
              allowClear
            >
              {types.map(type => (
                <Option key={type.value} value={type.value}>{type.label}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={24} md={10} style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={handleSearch}>搜索</Button>
              <Button onClick={handleReset}>重置</Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/classrooms/create')}
              >
                添加教室
              </Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={classrooms}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个教室`,
            onChange: (page, pageSize) => {
              fetchClassrooms(page, pageSize, searchText, selectedBuilding, selectedType);
            },
            onShowSizeChange: (current, size) => {
              fetchClassrooms(1, size, searchText, selectedBuilding, selectedType);
            },
          }}
        />
      </Card>
    </div>
  );
};

export default ClassroomListPage;

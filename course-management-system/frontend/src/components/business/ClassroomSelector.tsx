import React, { useState, useEffect } from 'react';
import { 
  Select, 
  Card, 
  Row, 
  Col, 
  Tag, 
  Space, 
  Input, 
  Button, 
  Tooltip,
  Badge,
  Empty,
  message
} from 'antd';
import {
  HomeOutlined,
  SearchOutlined,
  TeamOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { classroomAPI } from '../../services/api';

const { Option } = Select;

interface Classroom {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  type: 'lecture' | 'lab' | 'seminar' | 'computer' | 'multimedia';
  equipment: string[];
  isAvailable: boolean;
  currentUsage?: {
    isOccupied: boolean;
    courseName?: string;
    timeSlot?: string;
  };
}

interface ClassroomSelectorProps {
  value?: string;
  onChange?: (classroomId: string, classroom: Classroom) => void;
  disabled?: boolean;
  mode?: 'select' | 'card';
  showDetails?: boolean;
  filterByType?: string[];
  filterByCapacity?: { min?: number; max?: number };
  filterByBuilding?: string[];
  requiredEquipment?: string[];
  timeSlot?: { dayOfWeek: number; startTime: string; endTime: string };
}

const ClassroomSelector: React.FC<ClassroomSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  mode = 'select',
  showDetails = true,
  filterByType,
  filterByCapacity,
  filterByBuilding,
  requiredEquipment = [],
  timeSlot,
}) => {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [searchText, setSearchText] = useState('');
  const [selectedBuilding, setSelectedBuilding] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');

  // 模拟数据 - 已禁用，改为从 API 获取
  useEffect(() => {
    const fetchClassrooms = async () => {
      try {
        // 这里应该调用真实的 API
        const response = await classroomAPI.getClassrooms();
        setClassrooms(response.data);
      } catch (error) {
        console.error('获取教室列表失败:', error);
        message.error('获取教室列表失败，请联系管理员');
        setClassrooms([]);
      }
    };
    
    fetchClassrooms();
    
    /*
    // 模拟数据已禁用
    const mockClassrooms: Classroom[] = [
      {
        id: '1',
        name: 'A101',
        building: 'A栋',
        floor: 1,
        capacity: 120,
        type: 'lecture',
        equipment: ['投影仪', '音响', '黑板'],
        isAvailable: true,
        currentUsage: { isOccupied: false },
      },
      {
        id: '2',
        name: 'B205',
        building: 'B栋',
        floor: 2,
        capacity: 60,
        type: 'computer',
        equipment: ['电脑', '投影仪', '空调'],
        isAvailable: true,
        currentUsage: { 
          isOccupied: true, 
          courseName: '计算机基础',
          timeSlot: '10:00-11:40'
        },
      },
      {
        id: '3',
        name: 'C301',
        building: 'C栋',
        floor: 3,
        capacity: 40,
        type: 'seminar',
        equipment: ['白板', '投影仪', '圆桌'],
        isAvailable: false,
      },
      {
        id: '4',
        name: 'D102',
        building: 'D栋',
        floor: 1,
        capacity: 80,
        type: 'lab',
        equipment: ['实验台', '通风设备', '安全设备'],
        isAvailable: true,
        currentUsage: { isOccupied: false },
      },
      {
        id: '5',
        name: 'E203',
        building: 'E栋',
        floor: 2,
        capacity: 100,
        type: 'multimedia',
        equipment: ['多媒体设备', '音响', '投影仪', '空调'],
        isAvailable: true,
        currentUsage: { isOccupied: false },
      },
    ];
    setClassrooms(mockClassrooms);
    */
  }, []);

  const getTypeText = (type: string): string => {
    const typeMap = {
      lecture: '阶梯教室',
      lab: '实验室',
      seminar: '研讨室',
      computer: '机房',
      multimedia: '多媒体教室',
    };
    return typeMap[type as keyof typeof typeMap] || type;
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

  const isClassroomSuitable = (classroom: Classroom): boolean => {
    // 检查是否可用
    if (!classroom.isAvailable) return false;

    // 检查类型过滤
    if (filterByType && !filterByType.includes(classroom.type)) return false;

    // 检查容量过滤
    if (filterByCapacity) {
      if (filterByCapacity.min && classroom.capacity < filterByCapacity.min) return false;
      if (filterByCapacity.max && classroom.capacity > filterByCapacity.max) return false;
    }

    // 检查楼栋过滤
    if (filterByBuilding && !filterByBuilding.includes(classroom.building)) return false;

    // 检查必需设备
    if (requiredEquipment.length > 0) {
      const hasAllEquipment = requiredEquipment.every(equipment =>
        classroom.equipment.includes(equipment)
      );
      if (!hasAllEquipment) return false;
    }

    // 检查时间冲突（如果指定了时间段）
    if (timeSlot && classroom.currentUsage?.isOccupied) {
      return false;
    }

    return true;
  };

  const filteredClassrooms = classrooms.filter(classroom => {
    const matchesSearch = classroom.name.toLowerCase().includes(searchText.toLowerCase()) ||
                         classroom.building.toLowerCase().includes(searchText.toLowerCase());
    const matchesBuilding = !selectedBuilding || classroom.building === selectedBuilding;
    const matchesType = !selectedType || classroom.type === selectedType;
    
    return matchesSearch && matchesBuilding && matchesType;
  });

  const suitableClassrooms = filteredClassrooms.filter(isClassroomSuitable);
  const buildings = Array.from(new Set(classrooms.map(c => c.building)));
  const types = [
    { value: 'lecture', label: '阶梯教室' },
    { value: 'lab', label: '实验室' },
    { value: 'seminar', label: '研讨室' },
    { value: 'computer', label: '机房' },
    { value: 'multimedia', label: '多媒体教室' },
  ];

  const handleClassroomSelect = (classroomId: string) => {
    const classroom = classrooms.find(c => c.id === classroomId);
    if (classroom && onChange) {
      onChange(classroomId, classroom);
    }
  };

  if (mode === 'select') {
    return (
      <Select
        value={value}
        onChange={handleClassroomSelect}
        placeholder="选择教室"
        disabled={disabled}
        style={{ width: '100%' }}
        showSearch
        filterOption={(input, option) =>
          option?.children?.toString().toLowerCase().includes(input.toLowerCase()) ?? false
        }
      >
        {suitableClassrooms.map(classroom => (
          <Option key={classroom.id} value={classroom.id}>
            <Space>
              <HomeOutlined />
              <span>{classroom.name}</span>
              <Tag color={getTypeColor(classroom.type)}>
                {getTypeText(classroom.type)}
              </Tag>
              <span style={{ color: '#666' }}>
                {classroom.capacity}人
              </span>
              {classroom.currentUsage?.isOccupied && (
                <Tag color="red">使用中</Tag>
              )}
            </Space>
          </Option>
        ))}
      </Select>
    );
  }

  return (
    <Card
      title={
        <Space>
          <HomeOutlined />
          <span>选择教室</span>
          <Tag color="blue">{suitableClassrooms.length} 个可用</Tag>
        </Space>
      }
      size="small"
    >
      {/* 搜索和筛选 */}
      <Row gutter={[8, 8]} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Input
            placeholder="搜索教室名称或楼栋"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            size="small"
          />
        </Col>
        <Col span={6}>
          <Select
            placeholder="楼栋"
            value={selectedBuilding}
            onChange={setSelectedBuilding}
            allowClear
            size="small"
            style={{ width: '100%' }}
          >
            {buildings.map(building => (
              <Option key={building} value={building}>{building}</Option>
            ))}
          </Select>
        </Col>
        <Col span={6}>
          <Select
            placeholder="类型"
            value={selectedType}
            onChange={setSelectedType}
            allowClear
            size="small"
            style={{ width: '100%' }}
          >
            {types.map(type => (
              <Option key={type.value} value={type.value}>{type.label}</Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Button 
            size="small" 
            onClick={() => {
              setSearchText('');
              setSelectedBuilding('');
              setSelectedType('');
            }}
          >
            重置
          </Button>
        </Col>
      </Row>

      {/* 教室列表 */}
      {suitableClassrooms.length === 0 ? (
        <Empty 
          description="没有找到符合条件的教室"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <Row gutter={[8, 8]}>
          {suitableClassrooms.map(classroom => (
            <Col key={classroom.id} span={12}>
              <Card
                size="small"
                hoverable
                style={{
                  cursor: 'pointer',
                  border: value === classroom.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
                }}
                onClick={() => handleClassroomSelect(classroom.id)}
              >
                <div style={{ position: 'relative' }}>
                  {value === classroom.id && (
                    <CheckCircleOutlined
                      style={{
                        position: 'absolute',
                        top: '-4px',
                        right: '-4px',
                        color: '#1890ff',
                        fontSize: '16px',
                      }}
                    />
                  )}
                  
                  <div style={{ marginBottom: '8px' }}>
                    <Space>
                      <HomeOutlined style={{ color: '#1890ff' }} />
                      <span style={{ fontWeight: 'bold' }}>{classroom.name}</span>
                      <Badge
                        status={classroom.currentUsage?.isOccupied ? 'error' : 'success'}
                        text={classroom.currentUsage?.isOccupied ? '使用中' : '空闲'}
                      />
                    </Space>
                  </div>

                  <div style={{ marginBottom: '8px' }}>
                    <Space size="small">
                      <Tag color={getTypeColor(classroom.type)}>
                        {getTypeText(classroom.type)}
                      </Tag>
                      <span style={{ fontSize: '12px', color: '#666' }}>
                        {classroom.building} {classroom.floor}楼
                      </span>
                    </Space>
                  </div>

                  <div style={{ marginBottom: '8px' }}>
                    <Space size="small">
                      <TeamOutlined style={{ color: '#666' }} />
                      <span style={{ fontSize: '12px' }}>
                        容量: {classroom.capacity}人
                      </span>
                    </Space>
                  </div>

                  {showDetails && (
                    <div>
                      <div style={{ marginBottom: '4px' }}>
                        <Space size="small">
                          <SettingOutlined style={{ color: '#666' }} />
                          <span style={{ fontSize: '12px', color: '#666' }}>设备:</span>
                        </Space>
                      </div>
                      <Space wrap size="small">
                        {classroom.equipment.slice(0, 3).map(equipment => (
                          <Tag key={equipment} color="default">
                            {equipment}
                          </Tag>
                        ))}
                        {classroom.equipment.length > 3 && (
                          <Tooltip title={classroom.equipment.slice(3).join(', ')}>
                            <Tag color="default">
                              +{classroom.equipment.length - 3}
                            </Tag>
                          </Tooltip>
                        )}
                      </Space>
                    </div>
                  )}

                  {classroom.currentUsage?.isOccupied && (
                    <div style={{ 
                      marginTop: '8px', 
                      padding: '4px 8px', 
                      backgroundColor: '#fff2f0',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}>
                      <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: '4px' }} />
                      {classroom.currentUsage.courseName} ({classroom.currentUsage.timeSlot})
                    </div>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* 筛选条件说明 */}
      {(filterByType || filterByCapacity || filterByBuilding || requiredEquipment.length > 0) && (
        <div style={{ 
          marginTop: '12px', 
          padding: '8px', 
          backgroundColor: '#f6ffed',
          borderRadius: '4px',
          fontSize: '12px'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>筛选条件:</div>
          <Space wrap size="small">
            {filterByType && (
              <Tag color="blue">类型: {filterByType.map(getTypeText).join(', ')}</Tag>
            )}
            {filterByCapacity && (
              <Tag color="green">
                容量: {filterByCapacity.min || 0}-{filterByCapacity.max || '∞'}人
              </Tag>
            )}
            {filterByBuilding && (
              <Tag color="orange">楼栋: {filterByBuilding.join(', ')}</Tag>
            )}
            {requiredEquipment.length > 0 && (
              <Tag color="purple">设备: {requiredEquipment.join(', ')}</Tag>
            )}
          </Space>
        </div>
      )}
    </Card>
  );
};

export default ClassroomSelector;

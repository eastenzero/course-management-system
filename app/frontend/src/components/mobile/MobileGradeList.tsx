import React, { useState } from 'react';
import { Card, List, Space, Typography, Tag, Progress, Statistic, Row, Col, Select, Button } from 'antd';
import {
  TrophyOutlined,
  BookOutlined,
  CalendarOutlined,
  BarChartOutlined,
  StarOutlined
} from '@ant-design/icons';
import '../../styles/mobile.css';

const { Text, Title } = Typography;
const { Option } = Select;

interface GradeItem {
  id: number;
  course: {
    id: number;
    name: string;
    code: string;
    credits: number;
    semester: string;
  };
  score: number;
  grade: string;
  gpa_points: number;
  rank?: number;
  total_students?: number;
  components?: Array<{
    name: string;
    score: number;
    weight: number;
  }>;
}

interface GradeStatistics {
  total_credits: number;
  completed_credits: number;
  gpa: number;
  average_score: number;
  total_courses: number;
  passed_courses: number;
  semester_gpa?: { [semester: string]: number };
}

interface MobileGradeListProps {
  grades: GradeItem[];
  statistics: GradeStatistics;
  onGradeClick?: (gradeId: number) => void;
  className?: string;
}

const MobileGradeList: React.FC<MobileGradeListProps> = ({
  grades,
  statistics,
  onGradeClick,
  className = ''
}) => {
  const [selectedSemester, setSelectedSemester] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'score' | 'credits' | 'semester'>('semester');

  // 获取所有学期
  const getSemesters = () => {
    const semesters = Array.from(new Set(grades.map(g => g.course.semester)));
    return semesters.sort().reverse();
  };

  // 过滤和排序成绩
  const getFilteredAndSortedGrades = () => {
    let filtered = grades;
    
    if (selectedSemester !== 'all') {
      filtered = grades.filter(g => g.course.semester === selectedSemester);
    }

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.score - a.score;
        case 'credits':
          return b.course.credits - a.course.credits;
        case 'semester':
          return b.course.semester.localeCompare(a.course.semester);
        default:
          return 0;
      }
    });
  };

  // 获取成绩颜色
  const getGradeColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 80) return '#1890ff';
    if (score >= 70) return '#faad14';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  // 获取等级标签颜色
  const getGradeTagColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'green';
      case 'B': return 'blue';
      case 'C': return 'orange';
      case 'D': return 'gold';
      case 'F': return 'red';
      default: return 'default';
    }
  };

  // 渲染统计卡片
  const renderStatistics = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title="总GPA"
            value={statistics.gpa}
            precision={2}
            prefix={<TrophyOutlined />}
            valueStyle={{ color: statistics.gpa >= 3.5 ? '#52c41a' : statistics.gpa >= 3.0 ? '#1890ff' : '#faad14' }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="平均分"
            value={statistics.average_score}
            precision={1}
            suffix="分"
            prefix={<BarChartOutlined />}
            valueStyle={{ color: getGradeColor(statistics.average_score) }}
          />
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>学分进度</Text>
            <Progress
              type="circle"
              size={60}
              percent={Math.round((statistics.completed_credits / statistics.total_credits) * 100)}
              format={() => `${statistics.completed_credits}/${statistics.total_credits}`}
              strokeColor="#1890ff"
            />
          </div>
        </Col>
        <Col span={12}>
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>通过率</Text>
            <Progress
              type="circle"
              size={60}
              percent={Math.round((statistics.passed_courses / statistics.total_courses) * 100)}
              format={() => `${statistics.passed_courses}/${statistics.total_courses}`}
              strokeColor="#52c41a"
            />
          </div>
        </Col>
      </Row>
    </Card>
  );

  // 渲染筛选器
  const renderFilters = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
        <div>
          <Text style={{ fontSize: 12, marginRight: 8 }}>学期:</Text>
          <Select
            size="small"
            value={selectedSemester}
            onChange={setSelectedSemester}
            style={{ width: 120 }}
          >
            <Option value="all">全部学期</Option>
            {getSemesters().map(semester => (
              <Option key={semester} value={semester}>{semester}</Option>
            ))}
          </Select>
        </div>
        
        <div>
          <Text style={{ fontSize: 12, marginRight: 8 }}>排序:</Text>
          <Select
            size="small"
            value={sortBy}
            onChange={setSortBy}
            style={{ width: 100 }}
          >
            <Option value="semester">学期</Option>
            <Option value="score">成绩</Option>
            <Option value="credits">学分</Option>
          </Select>
        </div>
      </Space>
    </Card>
  );

  // 渲染成绩项
  const renderGradeItem = (grade: GradeItem) => (
    <Card 
      key={grade.id}
      className="mobile-grade-item"
      size="small"
      hoverable
      onClick={() => onGradeClick?.(grade.id)}
      style={{ marginBottom: 8 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <Title level={5} style={{ margin: 0, marginRight: 8 }}>
              {grade.course.name}
            </Title>
            <Tag color={getGradeTagColor(grade.grade)} size="small">
              {grade.grade}
            </Tag>
          </div>
          
          <Space size={16} style={{ marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <BookOutlined style={{ marginRight: 4, color: '#666' }} />
              <Text style={{ fontSize: 12 }}>{grade.course.code}</Text>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <StarOutlined style={{ marginRight: 4, color: '#666' }} />
              <Text style={{ fontSize: 12 }}>{grade.course.credits}学分</Text>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <CalendarOutlined style={{ marginRight: 4, color: '#666' }} />
              <Text style={{ fontSize: 12 }}>{grade.course.semester}</Text>
            </div>
          </Space>
          
          {grade.rank && grade.total_students && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              排名: {grade.rank}/{grade.total_students}
            </Text>
          )}
        </div>
        
        <div style={{ textAlign: 'right' }}>
          <div style={{ 
            fontSize: 24, 
            fontWeight: 600, 
            color: getGradeColor(grade.score),
            lineHeight: 1
          }}>
            {grade.score}
          </div>
          <Text type="secondary" style={{ fontSize: 11 }}>
            GPA: {grade.gpa_points.toFixed(1)}
          </Text>
        </div>
      </div>
      
      {grade.components && grade.components.length > 0 && (
        <div style={{ marginTop: 12, paddingTop: 8, borderTop: '1px solid #f0f0f0' }}>
          <Text type="secondary" style={{ fontSize: 11, marginBottom: 4, display: 'block' }}>
            成绩组成:
          </Text>
          <Space wrap size={[4, 4]}>
            {grade.components.map((component, index) => (
              <Tag key={index} size="small" color="blue">
                {component.name}: {component.score}分 ({component.weight}%)
              </Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );

  const filteredGrades = getFilteredAndSortedGrades();

  return (
    <div className={`mobile-grade-list ${className}`}>
      {renderStatistics()}
      {renderFilters()}
      
      <div>
        {filteredGrades.length > 0 ? (
          filteredGrades.map(renderGradeItem)
        ) : (
          <Card size="small" style={{ textAlign: 'center', color: '#999' }}>
            <Text type="secondary">暂无成绩记录</Text>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MobileGradeList;

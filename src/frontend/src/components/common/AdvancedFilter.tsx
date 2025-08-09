import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Select,
  Input,
  Button,
  Space,
  Row,
  Col,
  Slider,
  DatePicker,
  Checkbox,
  Radio,
  Tag,
  Divider,
  Typography,
  Collapse,
  Tooltip,
  InputNumber,
  Switch,
} from 'antd';
import {
  FilterOutlined,
  ClearOutlined,
  SaveOutlined,
  HistoryOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { RangePickerProps } from 'antd/es/date-picker';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { Title, Text } = Typography;
const { Panel } = Collapse;

// 筛选字段配置类型
export interface FilterFieldConfig {
  key: string;
  label: string;
  type: 'select' | 'multiSelect' | 'input' | 'range' | 'dateRange' | 'checkbox' | 'radio' | 'slider';
  options?: { value: any; label: string; disabled?: boolean }[];
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  defaultValue?: any;
  required?: boolean;
  width?: number | string;
  tooltip?: string;
}

// 筛选器组配置
export interface FilterGroupConfig {
  key: string;
  title: string;
  description?: string;
  fields: FilterFieldConfig[];
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export interface AdvancedFilterProps {
  groups: FilterGroupConfig[];
  onFilter: (filters: Record<string, any>) => void;
  onReset?: () => void;
  onSavePreset?: (name: string, filters: Record<string, any>) => void;
  presets?: { name: string; filters: Record<string, any> }[];
  loading?: boolean;
  className?: string;
}

const AdvancedFilter: React.FC<AdvancedFilterProps> = ({
  groups,
  onFilter,
  onReset,
  onSavePreset,
  presets = [],
  loading = false,
  className,
}) => {
  const [form] = Form.useForm();
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const [presetName, setPresetName] = useState('');
  const [showPresetInput, setShowPresetInput] = useState(false);

  // 渲染不同类型的筛选控件
  const renderFilterField = (field: FilterFieldConfig) => {
    const baseProps = {
      placeholder: field.placeholder,
      style: { width: field.width || '100%' },
    };

    switch (field.type) {
      case 'select':
        return (
          <Select {...baseProps} allowClear>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </Option>
            ))}
          </Select>
        );

      case 'multiSelect':
        return (
          <Select {...baseProps} mode="multiple" allowClear maxTagCount={3}>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </Option>
            ))}
          </Select>
        );

      case 'input':
        return <Input {...baseProps} allowClear />;

      case 'range':
        return (
          <Row gutter={8}>
            <Col span={11}>
              <InputNumber
                placeholder={`最小值`}
                min={field.min}
                max={field.max}
                style={{ width: '100%' }}
              />
            </Col>
            <Col span={2} className="text-center">
              <span className="text-gray-400">-</span>
            </Col>
            <Col span={11}>
              <InputNumber
                placeholder={`最大值`}
                min={field.min}
                max={field.max}
                style={{ width: '100%' }}
              />
            </Col>
          </Row>
        );

      case 'dateRange':
        return (
          <RangePicker
            {...baseProps}
            format="YYYY-MM-DD"
          />
        );

      case 'checkbox':
        return (
          <Checkbox.Group options={field.options} />
        );

      case 'radio':
        return (
          <Radio.Group options={field.options} />
        );

      case 'slider':
        return (
          <div className="px-2">
            <Slider
              range
              min={field.min || 0}
              max={field.max || 100}
              step={field.step || 1}
              marks={field.min && field.max ? {
                [field.min]: field.min.toString(),
                [field.max]: field.max.toString(),
              } : undefined}
            />
          </div>
        );

      default:
        return <Input {...baseProps} />;
    }
  };

  // 处理表单值变化
  const handleFormChange = (changedValues: any, allValues: any) => {
    setFilters(allValues);
    
    // 更新活跃筛选器列表
    const active = Object.keys(allValues).filter(key => {
      const value = allValues[key];
      return value !== undefined && value !== null && value !== '' && 
             (Array.isArray(value) ? value.length > 0 : true);
    });
    setActiveFilters(active);
  };

  // 应用筛选
  const handleFilter = () => {
    const validFilters = Object.entries(filters).reduce((acc, [key, value]) => {
      if (value !== undefined && value !== null && value !== '' && 
          (Array.isArray(value) ? value.length > 0 : true)) {
        acc[key] = value;
      }
      return acc;
    }, {} as Record<string, any>);
    
    onFilter(validFilters);
  };

  // 重置筛选
  const handleReset = () => {
    form.resetFields();
    setFilters({});
    setActiveFilters([]);
    if (onReset) {
      onReset();
    } else {
      onFilter({});
    }
  };

  // 应用预设筛选
  const applyPreset = (preset: { name: string; filters: Record<string, any> }) => {
    form.setFieldsValue(preset.filters);
    setFilters(preset.filters);
    onFilter(preset.filters);
  };

  // 保存预设
  const savePreset = () => {
    if (!presetName.trim()) {
      return;
    }
    
    if (onSavePreset) {
      onSavePreset(presetName, filters);
    }
    setPresetName('');
    setShowPresetInput(false);
  };

  // 移除单个筛选条件
  const removeFilter = (key: string) => {
    form.setFieldValue(key, undefined);
    const newFilters = { ...filters };
    delete newFilters[key];
    setFilters(newFilters);
    onFilter(newFilters);
  };

  return (
    <Card className={className} size="small">
      {/* 头部工具栏 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FilterOutlined className="text-gray-600" />
          <Title level={5} className="mb-0">
            高级筛选
          </Title>
          {activeFilters.length > 0 && (
            <Tag color="blue">{activeFilters.length} 个条件</Tag>
          )}
        </div>
        <Space>
          {presets.length > 0 && (
            <Select
              placeholder="选择预设"
              size="small"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => {
                if (value) {
                  const preset = presets.find(p => p.name === value);
                  if (preset) {
                    applyPreset(preset);
                  }
                }
              }}
            >
              {presets.map(preset => (
                <Option key={preset.name} value={preset.name}>
                  {preset.name}
                </Option>
              ))}
            </Select>
          )}
          <Tooltip title="重置筛选">
            <Button
              size="small"
              icon={<ClearOutlined />}
              onClick={handleReset}
              disabled={activeFilters.length === 0}
            >
              重置
            </Button>
          </Tooltip>
        </Space>
      </div>

      {/* 活跃筛选条件显示 */}
      {activeFilters.length > 0 && (
        <div className="mb-4">
          <Text type="secondary" className="text-sm block mb-2">
            当前筛选条件:
          </Text>
          <div className="flex flex-wrap gap-1">
            {activeFilters.map(key => {
              const field = groups.flatMap(g => g.fields).find(f => f.key === key);
              if (!field) return null;
              
              const value = filters[key];
              let displayValue = value;
              
              if (Array.isArray(value)) {
                displayValue = value.join(', ');
              } else if (field.options) {
                const option = field.options.find(opt => opt.value === value);
                displayValue = option?.label || value;
              }
              
              return (
                <Tag
                  key={key}
                  closable
                  onClose={() => removeFilter(key)}
                  color="blue"
                >
                  {field.label}: {displayValue}
                </Tag>
              );
            })}
          </div>
        </div>
      )}

      {/* 筛选表单 */}
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleFormChange}
        size="small"
      >
        <Collapse
          bordered={false}
          defaultActiveKey={groups.filter(g => !g.defaultCollapsed).map(g => g.key)}
        >
          {groups.map(group => (
            <Panel
              key={group.key}
              header={
                <div>
                  <strong>{group.title}</strong>
                  {group.description && (
                    <Text type="secondary" className="ml-2 text-sm">
                      {group.description}
                    </Text>
                  )}
                </div>
              }
              collapsible={group.collapsible !== false ? 'header' : 'disabled'}
            >
              <Row gutter={16}>
                {group.fields.map((field, index) => (
                  <Col
                    key={field.key}
                    xs={24}
                    sm={12}
                    md={field.width === '100%' ? 24 : 8}
                    className="mb-3"
                  >
                    <Form.Item
                      name={field.key}
                      label={
                        field.tooltip ? (
                          <Tooltip title={field.tooltip}>
                            <span>
                              {field.label}
                              {field.required && <span className="text-red-500 ml-1">*</span>}
                            </span>
                          </Tooltip>
                        ) : (
                          <span>
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                          </span>
                        )
                      }
                      rules={field.required ? [{ required: true, message: `请选择${field.label}` }] : []}
                    >
                      {renderFilterField(field)}
                    </Form.Item>
                  </Col>
                ))}
              </Row>
            </Panel>
          ))}
        </Collapse>
      </Form>

      <Divider style={{ margin: '16px 0' }} />

      {/* 底部操作栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {showPresetInput ? (
            <Space size="small">
              <Input
                size="small"
                placeholder="预设名称"
                value={presetName}
                onChange={(e) => setPresetName(e.target.value)}
                style={{ width: 120 }}
                onPressEnter={savePreset}
              />
              <Button size="small" type="primary" onClick={savePreset}>
                保存
              </Button>
              <Button size="small" onClick={() => setShowPresetInput(false)}>
                取消
              </Button>
            </Space>
          ) : (
            onSavePreset && activeFilters.length > 0 && (
              <Tooltip title="将当前筛选条件保存为预设">
                <Button
                  size="small"
                  icon={<SaveOutlined />}
                  onClick={() => setShowPresetInput(true)}
                >
                  保存预设
                </Button>
              </Tooltip>
            )
          )}
        </div>
        
        <Space>
          <Text type="secondary" className="text-sm">
            {activeFilters.length} 个筛选条件
          </Text>
          <Button
            type="primary"
            size="small"
            icon={<FilterOutlined />}
            loading={loading}
            onClick={handleFilter}
            disabled={activeFilters.length === 0}
          >
            应用筛选
          </Button>
        </Space>
      </div>
    </Card>
  );
};

export default AdvancedFilter;
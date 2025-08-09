import React, { useState } from 'react';
import {
  Card,
  Select,
  Input,
  Button,
  Space,
  Tag,
  Dropdown,
  Typography,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ClearOutlined,
  DownOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
} from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

// 快速筛选选项配置
export interface QuickFilterOption {
  key: string;
  label: string;
  value: any;
  count?: number;
  color?: string;
}

// 快速筛选配置
export interface QuickFilterConfig {
  key: string;
  label: string;
  type: 'select' | 'tags' | 'sort';
  options: QuickFilterOption[];
  placeholder?: string;
  multiple?: boolean;
  showCount?: boolean;
}

// 排序选项
export interface SortOption {
  key: string;
  label: string;
  direction: 'asc' | 'desc';
}

export interface QuickFilterProps {
  configs: QuickFilterConfig[];
  sortOptions?: SortOption[];
  onFilter: (filters: Record<string, any>) => void;
  onSort?: (sortKey: string, direction: 'asc' | 'desc') => void;
  onSearch?: (keyword: string) => void;
  searchPlaceholder?: string;
  showSearch?: boolean;
  className?: string;
  size?: 'small' | 'middle' | 'large';
}

const QuickFilter: React.FC<QuickFilterProps> = ({
  configs,
  sortOptions = [],
  onFilter,
  onSort,
  onSearch,
  searchPlaceholder = '搜索...',
  showSearch = true,
  className,
  size = 'middle',
}) => {
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [selectedTags, setSelectedTags] = useState<Record<string, any[]>>({});
  const [currentSort, setCurrentSort] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  // 处理筛选变化
  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    if (value === undefined || value === null || value === '' || 
        (Array.isArray(value) && value.length === 0)) {
      delete newFilters[key];
    }
    
    setFilters(newFilters);
    onFilter(newFilters);
  };

  // 处理标签选择
  const handleTagSelect = (configKey: string, option: QuickFilterOption) => {
    const currentTags = selectedTags[configKey] || [];
    const isSelected = currentTags.some(tag => tag.key === option.key);
    
    let newTags;
    if (isSelected) {
      // 取消选择
      newTags = currentTags.filter(tag => tag.key !== option.key);
    } else {
      // 添加选择
      newTags = [...currentTags, option];
    }
    
    const newSelectedTags = { ...selectedTags, [configKey]: newTags };
    setSelectedTags(newSelectedTags);
    
    // 更新筛选器
    handleFilterChange(configKey, newTags.map(tag => tag.value));
  };

  // 处理排序
  const handleSort = (sortKey: string, direction: 'asc' | 'desc') => {
    setCurrentSort({ key: sortKey, direction });
    if (onSort) {
      onSort(sortKey, direction);
    }
  };

  // 清空所有筛选
  const handleClearAll = () => {
    setFilters({});
    setSelectedTags({});
    setCurrentSort(null);
    onFilter({});
  };

  // 渲染筛选控件
  const renderFilterControl = (config: QuickFilterConfig) => {
    switch (config.type) {
      case 'select':
        return (
          <Select
            key={config.key}
            placeholder={config.placeholder || `选择${config.label}`}
            allowClear
            mode={config.multiple ? 'multiple' : undefined}
            maxTagCount={config.multiple ? 2 : undefined}
            style={{ minWidth: 120 }}
            size={size}
            value={filters[config.key]}
            onChange={(value) => handleFilterChange(config.key, value)}
          >
            {config.options.map(option => (
              <Option key={option.key} value={option.value}>
                <div className="flex items-center justify-between">
                  <span>{option.label}</span>
                  {config.showCount && option.count !== undefined && (
                    <Text type="secondary" className="text-xs ml-2">
                      {option.count}
                    </Text>
                  )}
                </div>
              </Option>
            ))}
          </Select>
        );

      case 'tags':
        const tags = selectedTags[config.key] || [];
        return (
          <div key={config.key} className="flex items-center gap-1">
            <Text type="secondary" className="text-sm whitespace-nowrap">
              {config.label}:
            </Text>
            <Space wrap size={4}>
              {config.options.map(option => {
                const isSelected = tags.some(tag => tag.key === option.key);
                return (
                  <Tag
                    key={option.key}
                    color={isSelected ? (option.color || 'blue') : 'default'}
                    className="cursor-pointer text-xs"
                    onClick={() => handleTagSelect(config.key, option)}
                  >
                    {option.label}
                    {config.showCount && option.count !== undefined && (
                      <span className="ml-1">({option.count})</span>
                    )}
                  </Tag>
                );
              })}
            </Space>
          </div>
        );

      default:
        return null;
    }
  };

  // 渲染排序下拉菜单
  const sortMenuItems = sortOptions.flatMap(option => [
    {
      key: `${option.key}_asc`,
      label: (
        <div className="flex items-center gap-2">
          <SortAscendingOutlined />
          {option.label} (升序)
        </div>
      ),
      onClick: () => handleSort(option.key, 'asc'),
    },
    {
      key: `${option.key}_desc`,
      label: (
        <div className="flex items-center gap-2">
          <SortDescendingOutlined />
          {option.label} (降序)
        </div>
      ),
      onClick: () => handleSort(option.key, 'desc'),
    },
  ]);

  const hasActiveFilters = Object.keys(filters).length > 0 || Object.keys(selectedTags).length > 0;

  return (
    <Card className={className} bodyStyle={{ paddingTop: 12, paddingBottom: 12 }}>
      <div className="flex flex-wrap items-center gap-3">
        {/* 搜索框 */}
        {showSearch && (
          <Search
            placeholder={searchPlaceholder}
            allowClear
            onSearch={onSearch}
            style={{ width: 240 }}
            size={size}
            className="flex-shrink-0"
          />
        )}

        {/* 筛选控件 */}
        {configs.map(config => renderFilterControl(config))}

        {/* 排序 */}
        {sortOptions.length > 0 && (
          <Dropdown
            menu={{ items: sortMenuItems }}
            trigger={['click']}
            placement="bottomLeft"
          >
            <Button size={size} className="flex items-center gap-1">
              <FilterOutlined />
              排序
              {currentSort && (
                <Text type="secondary" className="text-xs">
                  ({sortOptions.find(opt => opt.key === currentSort.key)?.label}{' '}
                  {currentSort.direction === 'asc' ? '升序' : '降序'})
                </Text>
              )}
              <DownOutlined />
            </Button>
          </Dropdown>
        )}

        {/* 清空按钮 */}
        {hasActiveFilters && (
          <Tooltip title="清空所有筛选">
            <Button
              size={size}
              icon={<ClearOutlined />}
              onClick={handleClearAll}
            >
              清空
            </Button>
          </Tooltip>
        )}

        {/* 活跃筛选统计 */}
        {hasActiveFilters && (
          <Text type="secondary" className="text-sm">
            {Object.keys(filters).length + Object.keys(selectedTags).length} 个筛选条件
          </Text>
        )}
      </div>

      {/* 已选标签显示 */}
      {Object.keys(selectedTags).length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <Text type="secondary" className="text-sm block mb-2">
            已选筛选:
          </Text>
          <div className="flex flex-wrap gap-1">
            {Object.entries(selectedTags).map(([configKey, tags]) =>
              tags.map(tag => (
                <Tag
                  key={`${configKey}_${tag.key}`}
                  closable
                  color={tag.color || 'blue'}
                  className="text-xs"
                  onClose={() => handleTagSelect(configKey, tag)}
                >
                  {tag.label}
                </Tag>
              ))
            )}
          </div>
        </div>
      )}
    </Card>
  );
};

export default QuickFilter;
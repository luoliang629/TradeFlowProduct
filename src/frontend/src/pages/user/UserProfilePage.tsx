import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Avatar,
  Upload,
  message,
  Tabs,
  Row,
  Col,
  Statistic,
  Badge,
  Descriptions,
  Progress,
  Select,
  Switch,
  Divider,
  Space,
  Alert,
} from 'antd';
import {
  UserOutlined,
  EditOutlined,
  SaveOutlined,
  UploadOutlined,
  CameraOutlined,
  BankOutlined,
  BarChartOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { apiService } from '../../services';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

interface UserStats {
  messages_sent: number;
  files_uploaded: number;
  credits_used: number;
  credits_remaining: number;
}

const UserProfilePage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user, loading } = useAppSelector(state => state.auth);
  const [form] = Form.useForm();
  const [companyForm] = Form.useForm();
  const [editing, setEditing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [activeTab, setActiveTab] = useState('profile');

  // 加载用户统计数据
  useEffect(() => {
    const loadUserStats = async () => {
      try {
        const response = await apiService.user.getUsageStats();
        if (response.success) {
          setUserStats(response.data);
        }
      } catch (error) {
        console.error('加载用户统计失败:', error);
      }
    };

    if (user) {
      loadUserStats();
      // 初始化表单数据
      form.setFieldsValue({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        company: user.company || '',
        position: user.position || '',
        bio: user.bio || '',
        location: user.location || '',
        timezone: user.timezone || 'Asia/Shanghai',
      });
    }
  }, [user, form]);

  // 处理头像上传
  const handleAvatarUpload = async (file: File) => {
    setUploading(true);
    try {
      // 这里应该调用头像上传API
      message.success('头像上传成功！');
    } catch (error) {
      message.error('头像上传失败');
    } finally {
      setUploading(false);
    }
  };

  // 保存个人资料
  const handleSaveProfile = async (values: any) => {
    try {
      const response = await apiService.user.updateProfile(values);
      if (response.success) {
        message.success('个人资料已更新');
        setEditing(false);
      }
    } catch (error) {
      message.error('保存失败，请重试');
    }
  };

  // 企业认证提交
  const handleCompanySubmit = async (values: any) => {
    try {
      message.info('企业认证申请已提交，我们将在3-5个工作日内处理');
    } catch (error) {
      message.error('提交失败，请重试');
    }
  };

  if (!user) {
    return (
      <div className="p-6">
        <Alert message="用户信息加载失败" type="error" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">个人中心</h1>
        <p className="text-gray-600">管理您的个人信息、企业认证和使用统计</p>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} size="large">
        {/* 个人资料 */}
        <TabPane
          tab={
            <span>
              <UserOutlined />
              个人资料
            </span>
          }
          key="profile"
        >
          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <Card>
                <div className="text-center">
                  <div className="relative inline-block mb-4">
                    <Avatar
                      size={120}
                      src={user.avatar}
                      icon={<UserOutlined />}
                      className="shadow-lg"
                    />
                    <Upload
                      showUploadList={false}
                      beforeUpload={(file) => {
                        handleAvatarUpload(file);
                        return false;
                      }}
                      accept="image/*"
                    >
                      <Button
                        icon={<CameraOutlined />}
                        shape="circle"
                        size="small"
                        className="absolute bottom-0 right-0"
                        loading={uploading}
                      />
                    </Upload>
                  </div>
                  <h3 className="text-lg font-medium mb-2">{user.name || '未设置姓名'}</h3>
                  <p className="text-gray-500 mb-4">{user.email}</p>
                  
                  {user.company && (
                    <Badge
                      status={user.verified ? 'success' : 'processing'}
                      text={user.verified ? '企业认证' : '待审核'}
                    />
                  )}
                </div>
              </Card>
            </Col>

            <Col xs={24} md={16}>
              <Card
                title="基本信息"
                extra={
                  <Button
                    type={editing ? 'primary' : 'default'}
                    icon={editing ? <SaveOutlined /> : <EditOutlined />}
                    onClick={() => {
                      if (editing) {
                        form.submit();
                      } else {
                        setEditing(true);
                      }
                    }}
                    loading={loading}
                  >
                    {editing ? '保存' : '编辑'}
                  </Button>
                }
              >
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSaveProfile}
                  disabled={!editing}
                >
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="name"
                        label="姓名"
                        rules={[{ required: true, message: '请输入姓名' }]}
                      >
                        <Input placeholder="请输入姓名" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="email"
                        label="邮箱"
                        rules={[
                          { required: true, message: '请输入邮箱' },
                          { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                      >
                        <Input placeholder="请输入邮箱" disabled />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item name="phone" label="电话">
                        <Input placeholder="请输入电话号码" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item name="position" label="职位">
                        <Input placeholder="请输入职位" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item name="location" label="所在地">
                        <Input placeholder="请输入所在地" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item name="timezone" label="时区">
                        <Select placeholder="请选择时区">
                          <Option value="Asia/Shanghai">北京时间 (UTC+8)</Option>
                          <Option value="America/New_York">纽约时间 (UTC-5)</Option>
                          <Option value="Europe/London">伦敦时间 (UTC+0)</Option>
                          <Option value="Asia/Tokyo">东京时间 (UTC+9)</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item name="bio" label="个人简介">
                    <TextArea
                      rows={4}
                      placeholder="简单介绍一下自己..."
                      showCount
                      maxLength={200}
                    />
                  </Form.Item>
                </Form>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 企业认证 */}
        <TabPane
          tab={
            <span>
              <BankOutlined />
              企业认证
            </span>
          }
          key="company"
        >
          <Card title="企业认证信息">
            {user.verified ? (
              <div>
                <div className="mb-4">
                  <CheckCircleOutlined className="text-green-500 mr-2" />
                  <span className="text-green-600 font-medium">企业认证已通过</span>
                </div>
                <Descriptions column={2} bordered>
                  <Descriptions.Item label="企业名称">{user.company}</Descriptions.Item>
                  <Descriptions.Item label="统一社会信用代码">91330100MA28F4A15X</Descriptions.Item>
                  <Descriptions.Item label="认证时间">2024-12-15</Descriptions.Item>
                  <Descriptions.Item label="认证状态">
                    <Badge status="success" text="已认证" />
                  </Descriptions.Item>
                </Descriptions>
              </div>
            ) : (
              <div>
                <Alert
                  message="企业认证说明"
                  description="通过企业认证后，您可以获得更多高级功能和更高的使用额度。认证过程通常需要3-5个工作日。"
                  type="info"
                  showIcon
                  className="mb-6"
                />
                
                <Form
                  form={companyForm}
                  layout="vertical"
                  onFinish={handleCompanySubmit}
                >
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="companyName"
                        label="企业名称"
                        rules={[{ required: true, message: '请输入企业名称' }]}
                      >
                        <Input placeholder="请输入完整的企业名称" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="creditCode"
                        label="统一社会信用代码"
                        rules={[{ required: true, message: '请输入统一社会信用代码' }]}
                      >
                        <Input placeholder="18位统一社会信用代码" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="businessLicense"
                        label="营业执照"
                        rules={[{ required: true, message: '请上传营业执照' }]}
                      >
                        <Upload
                          listType="picture-card"
                          accept="image/*"
                          beforeUpload={() => false}
                        >
                          <div>
                            <UploadOutlined />
                            <div className="mt-2">上传营业执照</div>
                          </div>
                        </Upload>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="contactPerson"
                        label="联系人"
                        rules={[{ required: true, message: '请输入联系人' }]}
                      >
                        <Input placeholder="企业联系人姓名" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" size="large">
                      提交认证申请
                    </Button>
                  </Form.Item>
                </Form>
              </div>
            )}
          </Card>
        </TabPane>

        {/* 使用统计 */}
        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              使用统计
            </span>
          }
          key="stats"
        >
          {userStats ? (
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="已发送消息"
                    value={userStats.messages_sent}
                    prefix={<UserOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="已上传文件"
                    value={userStats.files_uploaded}
                    prefix={<UploadOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="已使用积分"
                    value={userStats.credits_used}
                    prefix={<BarChartOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="剩余积分"
                    value={userStats.credits_remaining}
                    valueStyle={{ color: '#3f8600' }}
                    prefix={<CheckCircleOutlined />}
                  />
                </Card>
              </Col>

              <Col xs={24}>
                <Card title="积分使用情况">
                  <div className="mb-4">
                    <div className="flex justify-between mb-2">
                      <span>积分使用进度</span>
                      <span>
                        {userStats.credits_used} / {userStats.credits_used + userStats.credits_remaining}
                      </span>
                    </div>
                    <Progress
                      percent={Math.round((userStats.credits_used / (userStats.credits_used + userStats.credits_remaining)) * 100)}
                      status="active"
                    />
                  </div>
                  
                  <Alert
                    message="积分不足提醒"
                    description="当前剩余积分不足20%，建议及时续费以免影响使用。"
                    type="warning"
                    showIcon
                    action={
                      <Button size="small" type="primary">
                        立即续费
                      </Button>
                    }
                  />
                </Card>
              </Col>
            </Row>
          ) : (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-500">加载统计数据中...</p>
            </div>
          )}
        </TabPane>

        {/* 账户设置 */}
        <TabPane
          tab={
            <span>
              <SettingOutlined />
              账户设置
            </span>
          }
          key="settings"
        >
          <Card title="账户设置">
            <Space direction="vertical" size="large" className="w-full">
              <div>
                <h4 className="text-base font-medium mb-3">通知设置</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">邮件通知</div>
                      <div className="text-sm text-gray-500">接收重要更新和通知邮件</div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">消息推送</div>
                      <div className="text-sm text-gray-500">接收实时消息推送</div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>

              <Divider />

              <div>
                <h4 className="text-base font-medium mb-3">隐私设置</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">公开资料</div>
                      <div className="text-sm text-gray-500">允许其他用户查看您的基本资料</div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">在线状态</div>
                      <div className="text-sm text-gray-500">显示您的在线状态</div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>

              <Divider />

              <div>
                <h4 className="text-base font-medium mb-3">危险操作</h4>
                <Space>
                  <Button danger>更改密码</Button>
                  <Button danger>删除账户</Button>
                </Space>
              </div>
            </Space>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default UserProfilePage;
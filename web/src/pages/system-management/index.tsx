import { LlmIcon } from '@/components/svg-icon';
import { useTheme } from '@/components/theme-provider';
import { useSetModalState, useTranslate } from '@/hooks/common-hooks';
import { useSelectLlmList } from '@/hooks/llm-hooks';
import {
  DatabaseOutlined,
  PictureOutlined,
  PlusOutlined,
  ScanOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import {
  Button,
  Card,
  Col,
  Divider,
  Flex,
  Form,
  Input,
  Layout,
  List,
  Menu,
  Radio,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
  Upload,
} from 'antd';
import { useState } from 'react';
import SettingTitle from '../user-setting/components/setting-title';

const { Content, Sider } = Layout;
const { Text } = Typography;

const ModelCard = ({ item, clickApiKey }: any) => {
  const { visible, switchVisible } = useSetModalState();
  const { t } = useTranslate('setting');
  const { theme } = useTheme();

  const handleApiKeyClick = () => {
    clickApiKey(item.name);
  };

  const handleShowMoreClick = () => {
    switchVisible();
  };

  return (
    <List.Item>
      <Card className={theme === 'dark' ? 'bg-gray-800' : 'bg-white'}>
        <Row align={'middle'}>
          <Col span={12}>
            <Flex gap={'middle'} align="center">
              <LlmIcon name={item.name} />
              <Flex vertical gap={'small'}>
                <b>{item.name}</b>
                <Text>{item.tags}</Text>
              </Flex>
            </Flex>
          </Col>
          <Col span={12} className={'text-right'}>
            <Space size={'middle'}>
              <Button onClick={handleApiKeyClick}>
                <Flex align="center" gap={4}>
                  API-Key
                  <SettingOutlined />
                </Flex>
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>
    </List.Item>
  );
};

const ModelSettings = () => {
  const { myLlmList: llmList, loading } = useSelectLlmList();

  const clickApiKey = (llmFactory: string) => {
    // This will be implemented later
    console.log(llmFactory);
  };

  return (
    <Spin spinning={loading}>
      <List
        grid={{ gutter: 16, column: 1 }}
        dataSource={llmList}
        renderItem={(item) => (
          <ModelCard item={item} clickApiKey={clickApiKey}></ModelCard>
        )}
      />
    </Spin>
  );
};

const DatabaseSettings = () => {
  const [databaseType, setDatabaseType] = useState('mysql');
  const [damengForm] = Form.useForm();

  const handleDatabaseTypeChange = (value: string) => {
    setDatabaseType(value);
  };

  const handleDamengConnection = () => {
    damengForm.validateFields().then((values) => {
      console.log('Dameng connection values:', values);
      // Here you would typically make an API call to test the connection
    });
  };

  return (
    <Card title="数据库管理">
      <Form layout="vertical">
        <Form.Item label="数据库类型">
          <Radio.Group
            value={databaseType}
            onChange={(e) => handleDatabaseTypeChange(e.target.value)}
          >
            <Radio value="mysql">MySQL</Radio>
            <Radio value="dameng">达梦数据库</Radio>
          </Radio.Group>
        </Form.Item>

        {databaseType === 'mysql' && (
          <Card
            title="MySQL 连接信息"
            size="small"
            style={{ marginTop: 16 }}
            className="bg-gray-50"
            extra={<Tag color="green">当前使用</Tag>}
          >
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>地址：</Text>
                  <Text>localhost</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>端口：</Text>
                  <Text>3306</Text>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>用户名：</Text>
                  <Text>root</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>密码：</Text>
                  <Text type="secondary">••••••••</Text>
                </div>
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text strong>数据库名：</Text>
              <Text>ragflow</Text>
            </div>
          </Card>
        )}

        {databaseType === 'dameng' && (
          <Card
            title="达梦数据库连接配置"
            size="small"
            style={{ marginTop: 16 }}
          >
            <Form form={damengForm} layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="host"
                    label="地址"
                    rules={[{ required: true, message: '请输入数据库地址' }]}
                  >
                    <Input placeholder="请输入数据库地址" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="port"
                    label="端口"
                    rules={[{ required: true, message: '请输入端口号' }]}
                  >
                    <Input placeholder="请输入端口号" />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入用户名' }]}
                  >
                    <Input placeholder="请输入用户名" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="password"
                    label="密码"
                    rules={[{ required: true, message: '请输入密码' }]}
                  >
                    <Input.Password placeholder="请输入密码" />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item
                name="database"
                label="数据库名"
                rules={[{ required: true, message: '请输入数据库名' }]}
              >
                <Input placeholder="请输入数据库名" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={handleDamengConnection}>
                  连接确认
                </Button>
              </Form.Item>
            </Form>
          </Card>
        )}
      </Form>
    </Card>
  );
};

const OcrSettings = () => {
  const [ocrModel, setOcrModel] = useState('deepdoc');

  const handleOcrModelChange = (value: string) => {
    setOcrModel(value);
  };

  const handleSwitchModel = () => {
    console.log('Switching to MinerU model');
    // Here you would typically make an API call to switch the OCR model
  };

  return (
    <Card title="OCR管理">
      <Form layout="vertical">
        <Form.Item label="OCR模型类型">
          <Radio.Group
            value={ocrModel}
            onChange={(e) => handleOcrModelChange(e.target.value)}
          >
            <Radio value="deepdoc">DeepDoc</Radio>
            <Radio value="mineru">MinerU</Radio>
          </Radio.Group>
        </Form.Item>

        {ocrModel === 'deepdoc' && (
          <Card
            title="DeepDoc 模型信息"
            size="small"
            style={{ marginTop: 16 }}
            className="bg-gray-50"
            extra={<Tag color="green">当前使用</Tag>}
          >
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>模型地址：</Text>
                  <Text>http://localhost:8000/deepdoc</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>模型版本：</Text>
                  <Text>v1.0.0</Text>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>状态：</Text>
                  <Tag color="green">运行中</Tag>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <Text strong>支持语言：</Text>
                  <Text>中文、英文</Text>
                </div>
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text strong>模型描述：</Text>
              <Text>
                DeepDoc是一个高性能的OCR模型，支持多种文档格式的文本识别
              </Text>
            </div>
          </Card>
        )}

        {ocrModel === 'mineru' && (
          <Card title="MinerU 模型配置" size="small" style={{ marginTop: 16 }}>
            <div style={{ marginBottom: 16 }}>
              <Text>MinerU是一个轻量级的OCR模型，适合快速文本识别任务。</Text>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>模型地址：</Text>
              <Text>http://localhost:8001/mineru</Text>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>模型版本：</Text>
              <Text>v2.1.0</Text>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>支持语言：</Text>
              <Text>中文、英文、数字</Text>
            </div>
            <Form.Item>
              <Button type="primary" onClick={handleSwitchModel}>
                切换模型
              </Button>
            </Form.Item>
          </Card>
        )}
      </Form>
    </Card>
  );
};

const InterfaceSettings = () => {
  const [logoFileList, setLogoFileList] = useState([]);
  const [faviconFileList, setFaviconFileList] = useState([]);
  const [loginLogoFileList, setLoginLogoFileList] = useState([]);

  const handleUploadChange =
    (setter) =>
    ({ fileList }) => {
      setter(fileList);
    };

  const uploadButton = (
    <div>
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>上传</div>
    </div>
  );

  return (
    <Card bordered={false}>
      <div style={{ maxWidth: 800 }}>
        <div>
          <Typography.Title
            level={4}
            style={{ color: '#096dd9', marginBottom: '24px' }}
          >
            站点标识
          </Typography.Title>
          <Row align="middle" style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Typography.Text strong>LOGO</Typography.Text>
            </Col>
            <Col span={18}>
              <Upload
                listType="picture-card"
                fileList={logoFileList}
                onChange={handleUploadChange(setLogoFileList)}
                maxCount={1}
                beforeUpload={() => false}
              >
                {logoFileList.length === 0 && uploadButton}
              </Upload>
              <Typography.Text type="secondary">
                建议尺寸 200 * 50
              </Typography.Text>
            </Col>
          </Row>
          <Row align="middle" style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Typography.Text strong>浏览器Tab小图标</Typography.Text>
            </Col>
            <Col span={18}>
              <Upload
                listType="picture-card"
                fileList={faviconFileList}
                onChange={handleUploadChange(setFaviconFileList)}
                maxCount={1}
                beforeUpload={() => false}
              >
                {faviconFileList.length === 0 && uploadButton}
              </Upload>
              <Typography.Text type="secondary">
                建议尺寸 32 * 32, .ico格式
              </Typography.Text>
            </Col>
          </Row>
        </div>

        <Divider />

        <div>
          <Typography.Title
            level={4}
            style={{ color: '#096dd9', margin: '24px 0' }}
          >
            登录页面
          </Typography.Title>
          <Row align="middle" style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Typography.Text strong>登录界面LOGO</Typography.Text>
            </Col>
            <Col span={18}>
              <Upload
                listType="picture-card"
                fileList={loginLogoFileList}
                onChange={handleUploadChange(setLoginLogoFileList)}
                maxCount={1}
                beforeUpload={() => false}
              >
                {loginLogoFileList.length === 0 && uploadButton}
              </Upload>
              <Typography.Text type="secondary">
                建议尺寸 200 * 200
              </Typography.Text>
            </Col>
          </Row>
          <Row align="top" style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Typography.Text strong>登录页欢迎词</Typography.Text>
            </Col>
            <Col span={18}>
              <Input.TextArea
                rows={4}
                defaultValue={'欢迎使用 RAGFlow\n智能知识管理与AI助手平台'}
                style={{ maxWidth: 400 }}
              />
            </Col>
          </Row>
        </div>

        <Flex justify="flex-start" style={{ marginTop: 32 }}>
          <Button type="primary" size="large">
            保存更改
          </Button>
        </Flex>
      </div>
    </Card>
  );
};

const SystemManagementPage = () => {
  const [selectedKey, setSelectedKey] = useState('database');

  const renderContent = () => {
    switch (selectedKey) {
      case 'database':
        return <DatabaseSettings />;
      case 'ocr':
        return <OcrSettings />;
      case 'interface':
        return <InterfaceSettings />;
      case 'model':
        return <ModelSettings />;
      default:
        return <DatabaseSettings />;
    }
  };

  return (
    <Layout style={{ width: '100%', background: '#f0f2f5' }}>
      <Sider width={200} style={{ background: '#fff' }}>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={({ key }) => setSelectedKey(key)}
          style={{ height: '100%', borderRight: 0 }}
        >
          <Menu.Item key="database" icon={<DatabaseOutlined />}>
            数据库管理
          </Menu.Item>
          <Menu.Item key="ocr" icon={<ScanOutlined />}>
            OCR管理
          </Menu.Item>
          <Menu.Item key="interface" icon={<PictureOutlined />}>
            界面管理
          </Menu.Item>
        </Menu>
      </Sider>
      <Content style={{ padding: '24px', minHeight: 280 }}>
        <SettingTitle title={'系统管理'}></SettingTitle>
        <Divider />
        {renderContent()}
      </Content>
    </Layout>
  );
};

export default SystemManagementPage;

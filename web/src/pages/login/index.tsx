import logoWithText from '@/assets/logo-with-text.png';
import { useLogin, useRegister } from '@/hooks/login-hooks';
import { useInterfaceConfig, useSystemConfig } from '@/hooks/system-hooks';
import { rsaPsw } from '@/utils';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'umi';
import styles from './index.less';

const Login = () => {
  const [title, setTitle] = useState('login');
  const navigate = useNavigate();
  const { login, loading: signLoading } = useLogin();
  const { register, loading: registerLoading } = useRegister();
  const { t } = useTranslation('translation', { keyPrefix: 'login' });
  const loading = signLoading || registerLoading;
  const { config } = useSystemConfig();
  const { config: interfaceConfig } = useInterfaceConfig();
  const registerEnabled = config?.registerEnabled !== 0;
  const [form] = Form.useForm();

  useEffect(() => {
    form.validateFields(['nickname']);
  }, [form]);

  const changeTitle = () => {
    if (title === 'login' && !registerEnabled) {
      return;
    }
    setTitle((title) => (title === 'login' ? 'register' : 'login'));
  };

  const onCheck = async () => {
    try {
      const params = await form.validateFields();
      const rsaPassWord = rsaPsw(params.password) as string;
      if (title === 'login') {
        const code = await login({
          email: `${params.email}`.trim(),
          password: rsaPassWord,
        });
        if (code === 0) {
          navigate('/knowledge');
        }
      } else {
        const code = await register({
          nickname: params.nickname,
          email: params.email,
          password: rsaPassWord,
        });
        if (code === 0) {
          setTitle('login');
        }
      }
    } catch (errorInfo) {
      console.log('Failed:', errorInfo);
    }
  };

  // 动态logo URL
  const loginLogoUrl = interfaceConfig?.login_logo || logoWithText;
  const welcomeText =
    interfaceConfig?.login_welcome_text ||
    '欢迎使用 RAGFlow\n智能知识管理与AI助手平台';
  const loginTitle = interfaceConfig?.login_title || '欢迎使用 RAGFlow';

  return (
    <div className={styles.loginRoot}>
      <div className={styles.leftBrand}>
        <div className={styles.brandContent}>
          <div className={styles.logoCircle}>
            <img
              src={loginLogoUrl}
              alt="企业知识库LOGO"
              className={styles.logoImg}
            />
          </div>
          <h2 className={styles.brandTitle}>{loginTitle}</h2>
          <p className={styles.brandDesc}>{welcomeText.split('\n')[0]}</p>
          {welcomeText.split('\n').length > 1 && (
            <p className={styles.brandDesc}>{welcomeText.split('\n')[1]}</p>
          )}
        </div>
      </div>
      <div className={styles.rightForm}>
        <div className={styles.formCard}>
          <h2 className={styles.formTitle}>
            {title === 'login' ? t('login') : t('register')}
          </h2>
          <Form
            form={form}
            layout="vertical"
            name="dynamic_rule"
            className={styles.loginForm}
          >
            <Form.Item
              name="email"
              label={t('emailLabel')}
              rules={[{ required: true, message: t('emailPlaceholder') }]}
            >
              <Input
                size="large"
                placeholder={t('emailPlaceholder')}
                prefix={<UserOutlined />}
              />
            </Form.Item>
            {title === 'register' && (
              <Form.Item
                name="nickname"
                label={t('nicknameLabel')}
                rules={[{ required: true, message: t('nicknamePlaceholder') }]}
              >
                <Input
                  size="large"
                  placeholder={t('nicknamePlaceholder')}
                  prefix={<UserOutlined />}
                />
              </Form.Item>
            )}
            <Form.Item
              name="password"
              label={t('passwordLabel')}
              rules={[{ required: true, message: t('passwordPlaceholder') }]}
            >
              <Input.Password
                size="large"
                placeholder={t('passwordPlaceholder')}
                prefix={<LockOutlined />}
              />
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                className={styles.loginButton}
                onClick={onCheck}
                loading={loading}
                block
              >
                {title === 'login' ? t('login') : t('register')}
              </Button>
            </Form.Item>
            {registerEnabled && (
              <div className={styles.switchTip}>
                <a onClick={changeTitle}>
                  {title === 'login' ? t('register') : t('login')}
                </a>
              </div>
            )}
          </Form>
        </div>
      </div>
    </div>
  );
};

export default Login;

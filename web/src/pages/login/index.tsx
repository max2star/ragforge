import logoWithText from '@/assets/logo-with-text.png';
import { useLogin, useRegister } from '@/hooks/login-hooks';
import { useSystemConfig } from '@/hooks/system-hooks';
import { rsaPsw } from '@/utils';
import { Button, Checkbox, Form, Input } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Icon, useNavigate } from 'umi';
import styles from './index.less';

const Login = () => {
  const [title, setTitle] = useState('login');
  const navigate = useNavigate();
  const { login, loading: signLoading } = useLogin();
  const { register, loading: registerLoading } = useRegister();
  const { t } = useTranslation('translation', { keyPrefix: 'login' });
  const loading = signLoading || registerLoading;
  const { config } = useSystemConfig();
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

  return (
    <div className={styles.loginRoot}>
      <div className={styles.leftBrand}>
        <div className={styles.brandContent}>
          <div className={styles.logoCircle}>
            <img
              src={logoWithText}
              alt="企业知识库LOGO"
              className={styles.logoImg}
            />
          </div>
          <h2 className={styles.brandTitle}>欢迎使用 RAGFlow</h2>
          <p className={styles.brandDesc}>智能知识管理与AI助手平台</p>
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
                prefix={<Icon icon="local:github" />}
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
                  prefix={<Icon icon="local:github" />}
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
                prefix={<Icon icon="local:github" />} // 可换为锁图标
                onPressEnter={onCheck}
              />
            </Form.Item>
            {title === 'login' && (
              <Form.Item name="remember" valuePropName="checked">
                <Checkbox> {t('rememberMe')}</Checkbox>
              </Form.Item>
            )}
            <Button
              type="primary"
              block
              size="large"
              onClick={onCheck}
              loading={loading}
              className={styles.loginButton}
            >
              {title === 'login' ? t('login') : t('continue')}
            </Button>
            <div className={styles.switchTip}>
              {title === 'login' && registerEnabled && (
                <span>
                  {t('signInTip')}
                  <Button type="link" onClick={changeTitle}>
                    {t('signUp')}
                  </Button>
                </span>
              )}
              {title === 'register' && (
                <span>
                  {t('signUpTip')}
                  <Button type="link" onClick={changeTitle}>
                    {t('login')}
                  </Button>
                </span>
              )}
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
};

export default Login;

import { LanguageList, LanguageMap } from '@/constants/common';
import { useTranslate } from '@/hooks/common-hooks';
import { useChangeLanguage } from '@/hooks/logic-hooks';
import { useFetchUserInfo, useSaveSetting } from '@/hooks/user-setting-hooks';
import { Button, Divider, Form, Input, Select, Space, Spin } from 'antd';
import { useEffect } from 'react';
import SettingTitle from '../components/setting-title';
import { TimezoneList } from '../constants';
import { useValidateSubmittable } from '../hooks';
import parentStyles from '../index.less';
import styles from './index.less';

const { Option } = Select;

type FieldType = {
  nickname?: string;
  language?: string;
  email?: string;
  timezone?: string;
};

const tailLayout = {
  wrapperCol: { offset: 20, span: 4 },
};

const UserSettingProfile = () => {
  const { data: userInfo, loading } = useFetchUserInfo();
  const { saveSetting, loading: submitLoading } = useSaveSetting();
  const { form, submittable } = useValidateSubmittable();
  const { t } = useTranslate('setting');
  const changeLanguage = useChangeLanguage();

  const onFinish = async (values: any) => {
    saveSetting(values);
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
  };

  useEffect(() => {
    form.setFieldsValue(userInfo);
  }, [form, userInfo]);

  return (
    <section className={styles.profileWrapper}>
      <SettingTitle
        title={t('profile')}
        description={t('profileDescription')}
      ></SettingTitle>
      <Divider />
      <Spin spinning={loading}>
        <Form
          colon={false}
          name="basic"
          labelAlign={'left'}
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          style={{ width: '100%' }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          form={form}
          autoComplete="off"
        >
          <Form.Item<FieldType>
            label={t('username')}
            name="nickname"
            rules={[
              {
                required: true,
                message: t('usernameMessage'),
                whitespace: true,
              },
            ]}
          >
            <Input />
          </Form.Item>
          <Divider />
          <Form.Item<FieldType>
            label={t('language', { keyPrefix: 'common' })}
            name="language"
            rules={[
              {
                required: true,
                message: t('languageMessage', { keyPrefix: 'common' }),
              },
            ]}
          >
            <Select
              placeholder={t('languagePlaceholder', { keyPrefix: 'common' })}
              onChange={changeLanguage}
            >
              {LanguageList.map((x) => (
                <Option value={x} key={x}>
                  {LanguageMap[x as keyof typeof LanguageMap]}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Divider />
          <Form.Item<FieldType>
            label={t('timezone')}
            name="timezone"
            rules={[{ required: true, message: t('timezoneMessage') }]}
          >
            <Select placeholder={t('timezonePlaceholder')} showSearch>
              {TimezoneList.map((x) => (
                <Option value={x} key={x}>
                  {x}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Divider />
          <Form.Item label={t('email')}>
            <Form.Item<FieldType> name="email" noStyle>
              <Input disabled />
            </Form.Item>
            <p className={parentStyles.itemDescription}>
              {t('emailDescription')}
            </p>
          </Form.Item>
          <Form.Item
            {...tailLayout}
            shouldUpdate={(prevValues, curValues) =>
              prevValues.additional !== curValues.additional
            }
          >
            <Space>
              <Button htmlType="button">{t('cancel')}</Button>
              <Button
                type="primary"
                htmlType="submit"
                disabled={!submittable}
                loading={submitLoading}
              >
                {t('save', { keyPrefix: 'common' })}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Spin>
    </section>
  );
};

export default UserSettingProfile;

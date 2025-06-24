import { Button, Col, Divider, Row, Space, Spin, Typography } from 'antd';
import CategoryPanel from './category-panel';
import { ConfigurationForm } from './configuration';
import {
  useHandleChunkMethodChange,
  useSelectKnowledgeDetailsLoading,
  useSubmitKnowledgeConfiguration,
} from './hooks';

import { useTranslate } from '@/hooks/common-hooks';
import { useState } from 'react';
import styles from './index.less';

const { Title } = Typography;

const Configuration = () => {
  const loading = useSelectKnowledgeDetailsLoading();
  const { form, chunkMethod } = useHandleChunkMethodChange();
  const { t } = useTranslate('knowledgeConfiguration');
  const { submitKnowledgeConfiguration, submitLoading, navigateToDataset } =
    useSubmitKnowledgeConfiguration(form);

  const [editorValue, setEditorValue] = useState('{}');
  const [editorClassifierValue, setEditorClassifierValue] = useState('{}');

  const handleEditorValuesChange = (
    editorValue: string,
    editorClassifierValue: string,
  ) => {
    setEditorValue(editorValue);
    setEditorClassifierValue(editorClassifierValue);
  };

  const handleSubmit = () => {
    submitKnowledgeConfiguration(editorValue, editorClassifierValue);
  };

  return (
    <div className={styles.configurationWrapper}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <div>
          <Title level={5}>
            {t('configuration', { keyPrefix: 'knowledgeDetails' })}
          </Title>
          <p>{t('titleDescription')}</p>
        </div>
        <Space>
          <Button size={'middle'} onClick={navigateToDataset}>
            {t('cancel')}
          </Button>
          <Button
            type="primary"
            size={'middle'}
            loading={submitLoading}
            onClick={handleSubmit}
          >
            {t('save')}
          </Button>
        </Space>
      </div>
      <Divider></Divider>
      <Spin spinning={loading}>
        <Row gutter={32}>
          <Col span={8}>
            <ConfigurationForm
              form={form}
              onEditorValuesChange={handleEditorValuesChange}
            ></ConfigurationForm>
          </Col>
          <Col span={16}>
            <CategoryPanel chunkMethod={chunkMethod}></CategoryPanel>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default Configuration;

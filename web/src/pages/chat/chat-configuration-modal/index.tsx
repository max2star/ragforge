import { IModalManagerChildrenProps } from '@/components/modal-manager';
import {
  ModelVariableType,
  settledModelVariableMap,
} from '@/constants/knowledge';
import { useTranslate } from '@/hooks/common-hooks';
import { useFetchModelId } from '@/hooks/logic-hooks';
import { IDialog } from '@/interfaces/database/chat';
import { getBase64FromUploadFileList } from '@/utils/file-util';
import { removeUselessFieldsFromValues } from '@/utils/form';
import { Drawer, Flex, Form, Segmented, UploadFile } from 'antd';
import { SegmentedValue } from 'antd/es/segmented';
import camelCase from 'lodash/camelCase';
import { useEffect, useRef, useState } from 'react';
import { IPromptConfigParameters } from '../interface';
import AssistantSetting from './assistant-setting';
import ModelSetting from './model-setting';
import PromptEngine from './prompt-engine';

import styles from './index.less';

const layout = {
  labelCol: { span: 24 },
  wrapperCol: { span: 24 },
};

const validateMessages = {
  required: '${label} is required!',
  types: {
    email: '${label} is not a valid email!',
    number: '${label} is not a valid number!',
  },
  number: {
    range: '${label} must be between ${min} and ${max}',
  },
};

enum ConfigurationSegmented {
  AssistantSetting = 'Assistant Setting',
  PromptEngine = 'Prompt Engine',
  ModelSetting = 'Model Setting',
}

const segmentedMap = {
  [ConfigurationSegmented.AssistantSetting]: AssistantSetting,
  [ConfigurationSegmented.ModelSetting]: ModelSetting,
  [ConfigurationSegmented.PromptEngine]: PromptEngine,
};

interface IProps extends IModalManagerChildrenProps {
  initialDialog: IDialog;
  loading: boolean;
  onOk: (dialog: IDialog) => void;
  clearDialog: () => void;
}

const ChatConfigurationModal = ({
  visible,
  hideModal,
  initialDialog,
  loading,
  onOk,
  clearDialog,
}: IProps) => {
  const [form] = Form.useForm();
  const [hasError, setHasError] = useState(false);

  const [value, setValue] = useState<ConfigurationSegmented>(
    ConfigurationSegmented.AssistantSetting,
  );
  const promptEngineRef = useRef<Array<IPromptConfigParameters>>([]);
  const modelId = useFetchModelId();
  const { t } = useTranslate('chat');

  const handleOk = async () => {
    const values = await form.validateFields();
    if (hasError) {
      return;
    }
    const nextValues: any = removeUselessFieldsFromValues(
      values,
      'llm_setting.',
    );
    const emptyResponse = nextValues.prompt_config?.empty_response ?? '';

    const icon = await getBase64FromUploadFileList(values.icon);

    const finalValues = {
      dialog_id: initialDialog.id,
      ...nextValues,
      vector_similarity_weight: 1 - nextValues.vector_similarity_weight,
      prompt_config: {
        ...nextValues.prompt_config,
        parameters: promptEngineRef.current,
        empty_response: emptyResponse,
      },
      icon,
    };
    onOk(finalValues);
  };

  const handleSegmentedChange = (val: SegmentedValue) => {
    setValue(val as ConfigurationSegmented);
  };

  const handleModalAfterClose = () => {
    clearDialog();
    form.resetFields();
  };

  const title = (
    <Flex align="center" gap={10} style={{ height: 40 }}>
      <span
        style={{
          fontSize: 18,
          fontWeight: 600,
          lineHeight: 1,
          color: '#222',
          display: 'block',
        }}
      >
        {t('chatConfiguration')}
      </span>
    </Flex>
  );

  useEffect(() => {
    if (visible) {
      const icon = initialDialog.icon;
      let fileList: UploadFile[] = [];

      if (icon) {
        fileList = [{ uid: '1', name: 'file', thumbUrl: icon, status: 'done' }];
      }
      form.setFieldsValue({
        ...initialDialog,
        llm_setting:
          initialDialog.llm_setting ??
          settledModelVariableMap[ModelVariableType.Precise],
        icon: fileList,
        llm_id: initialDialog.llm_id ?? modelId,
        vector_similarity_weight:
          1 - (initialDialog.vector_similarity_weight ?? 0.3),
      });
    }
  }, [initialDialog, form, visible, modelId]);

  return (
    <Drawer
      title={title}
      width={688}
      open={visible}
      onClose={hideModal}
      placement="right"
      destroyOnClose
      afterOpenChange={(open) => {
        if (!open) {
          handleModalAfterClose();
        }
      }}
      styles={{
        body: {
          padding: 0,
          overflowY: 'hidden',
        },
      }}
      className={styles.flatModal}
      footer={
        <Flex justify="end" gap={8}>
          <button
            onClick={hideModal}
            style={{
              padding: '8px 16px',
              border: '1px solid #d9d9d9',
              borderRadius: '6px',
              background: '#fff',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            取消
          </button>
          <button
            onClick={handleOk}
            disabled={loading}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              background: '#1677ff',
              color: '#fff',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </Flex>
      }
    >
      <div
        style={{
          height: 'calc(100vh - 200px)',
          overflowY: 'auto',
          padding: '24px',
        }}
      >
        <div style={{ marginBottom: 24 }}>
          <Segmented
            size={'middle'}
            value={value}
            onChange={handleSegmentedChange}
            options={Object.values(ConfigurationSegmented).map((x) => ({
              label: t(camelCase(x)),
              value: x,
            }))}
            block
            style={{
              borderRadius: 8,
              backgroundColor: '#f5f5f5',
            }}
          />
        </div>
        <Form
          {...layout}
          name="nest-messages"
          form={form}
          style={{ maxWidth: '100%' }}
          validateMessages={validateMessages}
          colon={false}
          layout="vertical"
        >
          {(() => {
            const Element = segmentedMap[value];
            return (
              <Element
                show={true}
                form={form}
                setHasError={setHasError}
                {...(value === ConfigurationSegmented.ModelSetting
                  ? { initialLlmSetting: initialDialog.llm_setting, visible }
                  : {})}
                {...(value === ConfigurationSegmented.PromptEngine
                  ? { ref: promptEngineRef }
                  : {})}
              />
            );
          })()}
        </Form>
      </div>
    </Drawer>
  );
};

export default ChatConfigurationModal;

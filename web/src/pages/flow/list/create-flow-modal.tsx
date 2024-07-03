import { ReactComponent as NothingIcon } from '@/assets/svg/nothing.svg';
import { IModalManagerChildrenProps } from '@/components/modal-manager';
import { useTranslate } from '@/hooks/commonHooks';
import { useFetchFlowTemplates } from '@/hooks/flow-hooks';
import { useSelectItem } from '@/hooks/logicHooks';
import {
  Avatar,
  Card,
  Flex,
  Form,
  Input,
  Modal,
  Space,
  Typography,
} from 'antd';
import classNames from 'classnames';
import { useEffect } from 'react';
import styles from './index.less';

const { Title } = Typography;
interface IProps extends Omit<IModalManagerChildrenProps, 'showModal'> {
  loading: boolean;
  initialName: string;
  onOk: (name: string, templateId: string) => void;
  showModal?(): void;
}

const CreateFlowModal = ({
  visible,
  hideModal,
  loading,
  initialName,
  onOk,
}: IProps) => {
  const [form] = Form.useForm();
  const { t } = useTranslate('common');
  const { data: list } = useFetchFlowTemplates();
  const { selectedId, handleItemClick } = useSelectItem(list?.at(0)?.id);

  type FieldType = {
    name?: string;
  };

  const handleOk = async () => {
    const ret = await form.validateFields();

    return onOk(ret.name, selectedId);
  };

  useEffect(() => {
    if (visible) {
      form.setFieldValue('name', initialName);
    }
  }, [initialName, form, visible]);

  return (
    <Modal
      title={t('createFlow', { keyPrefix: 'flow' })}
      open={visible}
      onOk={handleOk}
      width={600}
      onCancel={hideModal}
      okButtonProps={{ loading }}
      confirmLoading={loading}
    >
      <Form
        name="basic"
        labelCol={{ span: 4 }}
        wrapperCol={{ span: 20 }}
        autoComplete="off"
        layout={'vertical'}
        form={form}
      >
        <Form.Item<FieldType>
          label={<b>{t('name')}</b>}
          name="name"
          rules={[{ required: true, message: t('namePlaceholder') }]}
        >
          <Input />
        </Form.Item>
      </Form>
      <Title level={5}>Create from templates</Title>
      <Flex vertical gap={16}>
        {list?.map((x) => (
          <Card
            key={x.id}
            className={classNames(styles.flowTemplateCard, {
              [styles.selectedFlowTemplateCard]: selectedId === x.id,
            })}
            onClick={handleItemClick(x.id)}
          >
            <Space size={'middle'}>
              {x.avatar ? (
                <Avatar size={40} icon={<NothingIcon />} src={x.avatar} />
              ) : (
                <NothingIcon width={40} height={30} />
              )}
              <b>{x.title}</b>
            </Space>
            <p>{x.description}</p>
          </Card>
        ))}
      </Flex>
    </Modal>
  );
};

export default CreateFlowModal;

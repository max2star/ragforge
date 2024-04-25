import { useFetchKnowledgeList } from '@/hooks/knowledgeHook';
import { IModalProps } from '@/interfaces/common';
import { Form, Modal, Select, SelectProps } from 'antd';

const ConnectToKnowledgeModal = ({
  visible,
  hideModal,
  onOk,
}: IModalProps<string[]>) => {
  const [form] = Form.useForm();
  const { list } = useFetchKnowledgeList();

  const options: SelectProps['options'] = list?.map((item) => ({
    label: item.name,
    value: item.id,
  }));

  const handleOk = async () => {
    const values = await form.getFieldsValue();
    const knowledgeIds = values.knowledgeIds ?? [];
    if (knowledgeIds.length > 0) {
      return onOk?.(knowledgeIds);
    }
  };

  return (
    <Modal
      title="Add to Knowledge Base"
      open={visible}
      onOk={handleOk}
      onCancel={hideModal}
    >
      <Form form={form}>
        <Form.Item
          name="knowledgeIds"
          noStyle
          rules={[
            {
              required: true,
              message: 'Please select your favourite colors!',
              type: 'array',
            },
          ]}
        >
          <Select
            mode="multiple"
            allowClear
            style={{ width: '100%' }}
            placeholder="Please select"
            options={options}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ConnectToKnowledgeModal;

import { Form, Input, Switch } from 'antd';
import { useLazyGetPayerFamilyByNameQuery } from './payerFamilyApi';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useAddPayerFamilyMutation } from './payerFamilyApi';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useCallback, useState } from 'react';
import { PayerFamily } from './types';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';

interface PayerFamilyCreateModalPropTypes {
  location: DocDocumentLocation | undefined;
  open?: boolean;
  onClose: () => void;
  onSave: (payerFamilyId: string) => void;
}

export const PayerFamilyCreateModal = (props: PayerFamilyCreateModalPropTypes) => {
  const { location, onClose, onSave, open } = props;
  const [form] = useForm();
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();
  const [addPayerFamily, { isLoading }] = useAddPayerFamilyMutation();
  const [customNameChecked, setCustomNameChecked] = useState<boolean>(false);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await addPayerFamily(values).unwrap();
      onSave(payerFamily._id);
      form.resetFields();
    },
    [addPayerFamily, onSave, form]
  );

  if (!location) {
    return <></>;
  }

  return (
    <Modal
      open={open}
      title={<>Add Payer Family for {location.site_name}</>}
      width="50%"
      okText="Submit"
      onOk={form.submit}
      onCancel={onClose}
    >
      <Form
        form={form}
        layout="vertical"
        disabled={isLoading}
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={onFinish}
      >
        <div className="flex">
          <div className="flex-1 mt-2 mb-4">
            <h3>Site</h3>
            <div>{location.site_name}</div>
          </div>
        </div>
        <Form.Item
          label="Name"
          name="name"
          rules={[
            { required: true, message: 'Please input a payer family name' },
            mustBeUnique(getPayerFamilyByName),
          ]}
        >
          <Input />
        </Form.Item>
        <Input.Group className="space-x-2 flex">
          Custom Name
          <br />
          <Switch
            checked={customNameChecked}
            onChange={setCustomNameChecked}
            checkedChildren="On"
            unCheckedChildren="Off"
          />
        </Input.Group>

        <PayerFamilyInfoForm />
      </Form>
    </Modal>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
function mustBeUnique(asyncValidator: Function) {
  return {
    async validator(_rule: Rule, value: string) {
      const { data: payerFamily } = await asyncValidator({ name: value });
      if (payerFamily) {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}

import { Form, Input } from 'antd';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import {
  useUpdatePayerFamilyMutation,
  useLazyGetPayerFamilyQuery,
  useLazyGetPayerFamilyByNameQuery,
} from './payerFamilyApi';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect } from 'react';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { PayerFamily } from './types';

interface PayerFamilyCreateModalPropTypes {
  location: DocDocumentLocation | undefined;
  payer_family_id: string;
  open?: boolean;
  onClose: () => void;
  onSave: (payer_family_id: string) => void;
}

export const PayerFamilyEditModal = (props: PayerFamilyCreateModalPropTypes) => {
  const { location, onClose, onSave, open, payer_family_id } = props;
  const [form] = useForm();
  const [getPayerFamily] = useLazyGetPayerFamilyQuery();
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();

  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();

  useEffect(() => {
    const fetchCurrentPayerFamilyVals = async () => {
      const { data } = await getPayerFamily(payer_family_id);
      if (data && open) {
        //conditional used to address: Warning: Instance created by `useForm` is not connected to any Form element. Forget to pass `form` prop?
        form.setFieldsValue({
          name: data?.name,
          payer_type: data.payer_type,
          payer_ids: data.payer_ids,
          channels: data.channels,
          benefits: data.benefits,
          plan_types: data.plan_types,
          regions: data.regions,
        });
      }
    };
    fetchCurrentPayerFamilyVals();
  }, [form, getPayerFamily, payer_family_id, open]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await updatePayerFamily({ ...values, _id: payer_family_id }).unwrap();
      onSave(payerFamily._id);
      form.resetFields();
    },
    [updatePayerFamily, onSave, form, payer_family_id]
  );

  if (!location) {
    return <></>;
  }

  return (
    <Modal
      open={open}
      title={<>Edit Payer Family for {location.site_name}</>}
      width="50%"
      okText="Submit"
      onOk={form.submit}
      onCancel={onClose}
      forceRender
      destroyOnClose={true}
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
        <Input.Group className="space-x-2 flex"></Input.Group>

        <PayerFamilyInfoForm />
      </Form>
    </Modal>
  );
};

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

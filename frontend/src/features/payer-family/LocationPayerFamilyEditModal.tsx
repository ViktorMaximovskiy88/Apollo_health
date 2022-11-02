import { Button, Checkbox, Drawer, Form, Input } from 'antd';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import {
  useUpdatePayerFamilyMutation,
  useLazyGetPayerFamilyQuery,
  useLazyGetPayerFamilyByNameQuery,
} from './payerFamilyApi';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect, useState } from 'react';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { PayerFamily } from './types';
import { CloseOutlined } from '@ant-design/icons';

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
  const [initialPayerOptions, setInitialPayerOptions] = useState<any>([]);

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
          custom_name: true,
        });
        setInitialPayerOptions(data.payer_ids);
      }
    };
    fetchCurrentPayerFamilyVals();
  }, [form, getPayerFamily, payer_family_id, open]);

  console.log(payer_family_id);
  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      let elem = values.payer_ids?.slice(0, 1);
      // @ts-ignore
      if (elem[0]?.label) {
        // @ts-ignore
        values.payer_ids = values.payer_ids?.map((val) => val.value);
      }
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
    <Drawer
      open={open}
      title={<>Edit Payer Family for {location.site_name}</>}
      width="30%"
      placement="left"
      closable={false}
      mask={false}
      extra={
        <Button type="text" onClick={onClose}>
          <CloseOutlined />
        </Button>
      }
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
          className="w-96 mr-5"
          dependencies={['custom_name']}
          rules={[
            { required: true, message: 'Please input a payer family name' },
            mustBeUnique(getPayerFamilyByName, payer_family_id),
          ]}
        >
          <Input />
        </Form.Item>
        {form.getFieldValue('custom_name') ? 'Custom name will be generated on submission' : ''}
        <Input.Group className="space-x-2 flex">
          <Form.Item valuePropName="checked" name="custom_name">
            <Checkbox>Auto Generate</Checkbox>
          </Form.Item>
        </Input.Group>

        <PayerFamilyInfoForm initialPayerOptions={initialPayerOptions} />

        <div className="space-x-2 flex justify-end">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" onClick={form.submit} loading={isLoading}>
            Submit
          </Button>
        </div>
      </Form>
    </Drawer>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
function mustBeUnique(asyncValidator: Function, currentPayerFamilyId: string) {
  return {
    async validator(_rule: Rule, value: string) {
      const { data: payerFamily } = await asyncValidator({ name: value });

      if (!payerFamily) {
        return Promise.resolve();
      }
      if (
        currentPayerFamilyId === payerFamily._id &&
        value !== payerFamily.name.toLowerCase() &&
        value !== payerFamily.name.toUpperCase()
      ) {
        return Promise.resolve();
      } else {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
    },
  };
}

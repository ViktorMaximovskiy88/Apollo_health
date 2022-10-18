import { Form, Input, Select } from 'antd';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useUpdatePayerFamilyMutation, useLazyGetPayerFamilyQuery } from './payerFamilyApi';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect } from 'react';
import { RemoteSelect } from '../../components';
import { useLazyGetPayerBackbonesQuery } from '../payer-backbone/payerBackboneApi';
import {
  payerTypeOptions,
  channelOptions,
  benefitOptions,
  planTypeOptions,
  regionOptions,
} from './payerLevels';
import { PayerFamily } from './types';

interface PayerFamilyCreateModalPropTypes {
  location: DocDocumentLocation | undefined;
  payerFamilyId: string;
  open?: boolean;
  onClose: () => void;
  onSave: (payerFamilyId: string) => void;
}

function PayerInfo() {
  const [getPayers] = useLazyGetPayerBackbonesQuery();
  const form = Form.useFormInstance();
  const payerType = Form.useWatch('payer_type');

  useEffect(() => {
    form.setFieldsValue({ payer_ids: [] });
  }, [form, payerType]);

  const payerOptions = useCallback(
    async (search: string) => {
      if (!payerType) return [];
      const { data } = await getPayers({
        type: payerType,
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((payer) => ({ label: payer.name, value: payer.l_id }));
    },
    [getPayers, payerType]
  );
  return (
    <div className="mt-4">
      <h2>Payer</h2>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Payer Type" name={'payer_type'} className="w-48">
          <Select options={payerTypeOptions} />
        </Form.Item>
        <Form.Item label="Payers" name={'payer_ids'} className="grow">
          <RemoteSelect mode="multiple" className="w-full" fetchOptions={payerOptions} />
        </Form.Item>
      </Input.Group>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Channel" name={'channels'} className="w-full">
          <Select mode="multiple" options={channelOptions} />
        </Form.Item>
        <Form.Item label="Benefit" name={'benefits'} className="w-full">
          <Select mode="multiple" options={benefitOptions} />
        </Form.Item>
        <Form.Item label="Plan Types" name={'plan_types'} className="w-full">
          <Select mode="multiple" options={planTypeOptions} />
        </Form.Item>
        <Form.Item label="Region" name={'regions'} className="w-full">
          <Select mode="multiple" options={regionOptions} />
        </Form.Item>
      </Input.Group>
    </div>
  );
}

export const PayerFamilyEditModal = (props: PayerFamilyCreateModalPropTypes) => {
  const { location, onClose, onSave, open, payerFamilyId } = props;
  const [form] = useForm();
  const [getPayerFamily] = useLazyGetPayerFamilyQuery();
  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();

  useEffect(() => {
    const fetchCurrentPayerFamilyVals = async () => {
      const { data } = await getPayerFamily(payerFamilyId);
      if (data && open) {
        // used to address: Warning: Instance created by `useForm` is not connected to any Form element. Forget to pass `form` prop?
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
  }, [form, getPayerFamily, payerFamilyId, open]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await updatePayerFamily({ ...values, _id: payerFamilyId }).unwrap();
      onSave(payerFamily._id);
      form.resetFields();
    },
    [updatePayerFamily, onSave, form, payerFamilyId]
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
          rules={[{ required: true, message: 'Please input a payer family name' }]}
        >
          <Input />
        </Form.Item>
        <Input.Group className="space-x-2 flex"></Input.Group>

        <PayerInfo />
      </Form>
    </Modal>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch

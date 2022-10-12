import { Form, Input, Select } from 'antd';
import { useLazyGetPayerFamilyByNameQuery } from './payerFamilyApi';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useAddPayerFamilyMutation } from './payerFamilyApi';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useCallback, useEffect } from 'react';
import { RemoteSelect } from '../../components';
import { useLazyGetPayerBackbonesQuery } from '../payer-backbone/payerBackboneApi';
import {
  payerTypeOptions,
  channelOptions,
  benefitOptions,
  planTypeOptions,
  regionOptions,
  fieldGroupsOptions,
} from './payerLevels';

interface PayerFamilyCreateModalPropTypes {
  documentType: string;
  location: DocDocumentLocation | undefined;
  open?: boolean;
  onClose: () => void;
  onSave: (payerFamilyId: string) => void;
}

function PayerInfo() {
  const [getPayers] = useLazyGetPayerBackbonesQuery();
  const form = Form.useFormInstance();
  const payerType = Form.useWatch(['payer_type']);

  useEffect(() => {
    form.setFieldsValue({ payer_type: { payer_ids: [] } });
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
        <Form.Item label="Payer Type" name={['payer_type']} className="w-48">
          <Select options={payerTypeOptions} />
        </Form.Item>
        <Form.Item label="Payers" name={['payer_ids']} className="grow">
          <RemoteSelect mode="multiple" className="w-full" fetchOptions={payerOptions} />
        </Form.Item>
      </Input.Group>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Channel" name={['channels']} className="w-full">
          <Select mode="multiple" options={channelOptions} />
        </Form.Item>
        <Form.Item label="Benefit" name={['benefits']} className="w-full">
          <Select mode="multiple" options={benefitOptions} />
        </Form.Item>
        <Form.Item label="Plan Types" name={['plan_types']} className="w-full">
          <Select mode="multiple" options={planTypeOptions} />
        </Form.Item>
        <Form.Item label="Region" name={['regions']} className="w-full">
          <Select mode="multiple" options={regionOptions} />
        </Form.Item>
      </Input.Group>
    </div>
  );
}

export const PayerFamilyCreateModal = (props: PayerFamilyCreateModalPropTypes) => {
  let legacyRelevanceOptions = [
    { label: 'Editor Manual', value: 'EDITOR_MANUAL' },
    { label: 'Editor Automated ', value: 'EDITOR_AUTOMATED' },
    { label: 'PAR', value: 'PAR' },
    { label: 'N/A', value: 'N/A' },
  ];
  const { documentType, location, onClose, onSave, open } = props;
  const [form] = useForm();
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();
  const [addPayerFamily, { isLoading, data, isSuccess }] = useAddPayerFamilyMutation();

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data._id);
      form.resetFields();
    }
  }, [isSuccess, data]);

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
        onFinish={(values: any) => {
          addPayerFamily({
            ...values,
            document_type: documentType,
          });
        }}
      >
        <div className="flex">
          <div className="flex-1 mt-2 mb-4">
            <h3>Site</h3>
            <div>{location.site_name}</div>
          </div>

          <div className="flex-1 mt-2 mb-4">
            <h3>Document Type</h3>
            <div>{documentType}</div>
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
        <PayerInfo />
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
        return Promise.reject(
          `Payer family name "${payerFamily.name}" already exists on this site`
        );
      }
      return Promise.resolve();
    },
  };
}

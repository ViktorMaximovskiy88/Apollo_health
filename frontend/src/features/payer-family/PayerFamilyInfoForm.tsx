import { Form, Input, Select } from 'antd';
import { useCallback, useEffect } from 'react';
import { RemoteSelect } from '../../components';
import { useLazyGetPayerBackbonesQuery } from '../payer-backbone/payerBackboneApi';
import {
  benefitOptions,
  channelOptions,
  payerTypeOptions,
  planTypeOptions,
  regionOptions,
} from './payerLevels';

export const PayerFamilyInfoForm = () => {
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
};

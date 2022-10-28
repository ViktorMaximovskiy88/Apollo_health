import { Form, Input, Select } from 'antd';
import { FormInstance, Rule } from 'antd/lib/form';
import { useCallback, useEffect } from 'react';
import { RemoteSelect } from '../../components';
import { useLazyGetPayerBackbonesQuery } from '../payer-backbone/payerBackboneApi';
import {
  benefitOptions,
  channelOptions,
  backBoneLevelOptions,
  planTypeOptions,
  regionOptions,
} from './payerLevels';

interface PayerFamilyInfoFormProps {
  initialPayerOptions?: [Payer];
}

interface Payer {
  label: string;
  value: number;
}

export const PayerFamilyInfoForm = (props: PayerFamilyInfoFormProps) => {
  const { initialPayerOptions } = props;
  const [getPayers] = useLazyGetPayerBackbonesQuery();
  const form = Form.useFormInstance();
  const payerType = Form.useWatch('payer_type');

  useEffect(() => {
    form.setFieldsValue({ payer_ids: initialPayerOptions });
  }, [form, payerType, initialPayerOptions]);

  const backBoneValueOptions = useCallback(
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
        <Form.Item
          initialValue={'Not Selected'}
          label="Backbone Level"
          name={'payer_type'}
          className="w-48"
        >
          <Select defaultActiveFirstOption={true} options={backBoneLevelOptions} />
        </Form.Item>
        <Form.Item
          rules={[{ required: false }, mustHaveOnePayerValue(form)]}
          label="Backbone Values"
          name={'payer_ids'}
          className="w-80"
        >
          <RemoteSelect
            mode="multiple"
            disabled={
              !form.getFieldValue('payer_type') ||
              form.getFieldValue('payer_type') === 'Not Selected'
            }
            className="w-full"
            fetchOptions={backBoneValueOptions}
          />
        </Form.Item>
      </Input.Group>
      <Input.Group className="space-x-1 flex flex-wrap">
        <Form.Item
          rules={[{ required: false }, mustHaveOnePayerValue(form)]}
          label="Channel"
          name={'channels'}
          className="w-80"
        >
          <Select mode="multiple" options={channelOptions} />
        </Form.Item>
        <Form.Item
          rules={[{ required: false }, mustHaveOnePayerValue(form)]}
          label="Benefit"
          name={'benefits'}
          className="w-64"
        >
          <Select mode="multiple" options={benefitOptions} />
        </Form.Item>
        <Form.Item
          rules={[{ required: false }, mustHaveOnePayerValue(form)]}
          label="Plan Types"
          name={'plan_types'}
          className="w-40"
        >
          <Select mode="multiple" options={planTypeOptions} />
        </Form.Item>
        <Form.Item
          rules={[{ required: false }, mustHaveOnePayerValue(form)]}
          label="Region"
          name={'regions'}
          className="w-40"
        >
          <Select mode="multiple" options={regionOptions} />
        </Form.Item>
      </Input.Group>
    </div>
  );
};

function mustHaveOnePayerValue(form: FormInstance) {
  const { payer_ids, channels, regions, plan_types, benefits } = form.getFieldsValue(true);
  return {
    async validator(_rule: Rule) {
      if (
        payer_ids?.length ||
        channels?.length ||
        regions?.length ||
        plan_types?.length ||
        benefits?.length
      ) {
        return await Promise.resolve();
      } else {
        return await Promise.reject('One Payer Value required');
      }
    },
  };
}

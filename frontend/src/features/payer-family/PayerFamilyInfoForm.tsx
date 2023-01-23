import { Button, Form, Input, Modal, Select } from 'antd';
import { Rule } from 'antd/lib/form';
import { useCallback, useEffect, useState } from 'react';
import { RemoteSelect } from '../../components';
import {
  useGetPayerBackbonesQuery,
  useLazyGetPayerBackbonesQuery,
} from '../payer-backbone/payerBackboneApi';
import { useConvertPayerFamilyDataQuery } from './payerFamilyApi';
import {
  benefitOptions,
  channelOptions,
  backBoneLevelOptions,
  planTypeOptions,
  regionOptions,
} from './payerLevels';

function PayerIdsSelector() {
  const payerType = Form.useWatch('payer_type');
  const [getPayers] = useLazyGetPayerBackbonesQuery();
  const backBoneValueOptions = useCallback(
    async (search: string) => {
      if (!payerType) {
        return [];
      }
      const { data } = await getPayers({
        type: payerType,
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((payer) => ({ label: payer.name, value: payer.l_id.toString() }));
    },
    [getPayers, payerType]
  );

  const initialPayerIds = Form.useWatch('payer_ids');
  const { data: payers } = useGetPayerBackbonesQuery(
    {
      type: payerType,
      filterValue: [{ name: 'l_id', operator: 'eq', type: 'number', value: initialPayerIds }],
    },
    { skip: !payerType || !initialPayerIds || payerType === 'Not Selected' }
  );
  const initialPayerOptions =
    payers?.data.map((p) => ({ label: p.name, value: p.l_id.toString() })) || [];

  return (
    <Form.Item
      rules={[{ validator: (_rule, value) => backboneValueValidator(value, payerType) }]}
      label="Backbone Values"
      name="payer_ids"
      className="w-80"
    >
      <RemoteSelect
        mode="multiple"
        disabled={payerType === 'Not Selected' ? true : false}
        className="w-full"
        fetchOptions={backBoneValueOptions}
        initialOptions={initialPayerOptions}
      />
    </Form.Item>
  );
}

export function MatchingPlansModal() {
  const [open, setOpen] = useState(false);
  const onClick = useCallback(() => setOpen(true), [setOpen]);
  const onClose = useCallback(() => setOpen(false), [setOpen]);
  const name = Form.useWatch('name') || '';
  const regions = Form.useWatch('regions');
  const payer_type = Form.useWatch('payer_type');
  const payer_ids = Form.useWatch('payer_ids');
  const plan_types = Form.useWatch('plan_types');
  const channels = Form.useWatch('channels');
  const benefits = Form.useWatch('benefits');
  const pf = { name, payer_type, payer_ids, plan_types, channels, benefits, regions };
  const { data: convertedPf, isError } = useConvertPayerFamilyDataQuery(
    { payerType: 'plan', body: pf },
    { skip: !open }
  );
  const { data: planNames } = useGetPayerBackbonesQuery(
    {
      type: 'plan',
      filterValue: [
        {
          name: 'l_id',
          operator: 'eq',
          type: 'number',
          value: convertedPf?.payer_ids.map((x) => +x).slice(0, 100),
        },
      ],
      sortInfo: { name: 'name', dir: 1 },
    },
    { skip: !open || !convertedPf || isError }
  );

  return (
    <>
      <Button className="pl-0" type="link" onClick={onClick}>
        See Matching Plans
      </Button>
      <Modal
        title="Matching Plans"
        open={open}
        onOk={onClose}
        onCancel={onClose}
        cancelButtonProps={{ className: 'hidden' }}
      >
        {isError ? (
          'No Plans match this Payer Family'
        ) : (
          <>
            <div className="max-h-72 overflow-auto">
              <table className="w-full">
                <tbody>
                  {planNames?.data.map((plan) => {
                    return (
                      <tr className="even:bg-gray-100" key={plan.l_id}>
                        <td className="p-2">{plan.l_id}</td>
                        <td>{plan.name}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {planNames?.data.length === 100 ? (
              <div className="pt-2">Note: Only the first 100 plans are shown</div>
            ) : null}
          </>
        )}
      </Modal>
    </>
  );
}

// add props and pass handleChange prop

export const PayerFamilyInfoForm = () => {
  const form = Form.useFormInstance();

  useEffect(() => {
    form.setFieldValue('payer_type', 'Not Selected');
  }, [form]);

  const handlePlanChange = useCallback(() => {
    form.setFieldsValue({ payer_ids: [] });
  }, [form]);

  return (
    <div className="mt-4">
      <h2>Payer</h2>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Backbone Level" name="payer_type" className="w-48">
          <Select
            defaultActiveFirstOption={true}
            defaultValue={'Not Selected'}
            onChange={handlePlanChange}
            options={backBoneLevelOptions}
          />
        </Form.Item>
        <PayerIdsSelector />
      </Input.Group>
      <Input.Group className="space-x-1 flex flex-wrap">
        <Form.Item label="Channel" name={'channels'} className="w-80">
          <Select mode="multiple" options={channelOptions} />
        </Form.Item>
        <Form.Item label="Benefit" name="benefits" className="w-64">
          <Select mode="multiple" options={benefitOptions} />
        </Form.Item>
        <Form.Item label="Plan Types" name="plan_types" className="w-40">
          <Select mode="multiple" options={planTypeOptions} />
        </Form.Item>
        <Form.Item label="Region" name={'regions'} className="w-40">
          <Select mode="multiple" options={regionOptions} />
        </Form.Item>
      </Input.Group>
      <MatchingPlansModal />
    </div>
  );
};

function backboneValueValidator(payerValue: string[], payerType: string | null) {
  if (payerValue.length === 0 && payerType !== 'Not Selected') {
    return Promise.reject('Backbone value is required');
  }
  return Promise.resolve();
}

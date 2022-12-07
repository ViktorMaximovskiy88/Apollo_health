import { Form, FormInstance, Input, Select } from 'antd';
import { useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { RemoteSelect } from '../../components';
import { channelOptions, planTypeOptions, regionOptions } from '../payer-family/payerLevels';
import { useGetPayerBackboneByLIdQuery, useLazyGetPayerBackbonesQuery } from './payerBackboneApi';
import { PayerBackbone } from './types';

const NationalOptions = [
  { value: true, label: 'true' },
  { value: false, label: 'false' },
];

function PayerSelect({ field, payerType }: { field: string; payerType: string }) {
  const id = Form.useWatch(field);
  const { data: payer } = useGetPayerBackboneByLIdQuery({ id, payerType }, { skip: !id });
  const [getPayers] = useLazyGetPayerBackbonesQuery();

  const fetchOptions = useCallback(
    async (search: string) => {
      const { data } = await getPayers({
        type: payerType,
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((p) => ({ key: p.l_id, label: p.name, value: p.l_id }));
    },
    [payerType, getPayers]
  );

  const initialOptions = payer ? [{ value: payer.l_id, label: payer.name }] : [];
  return (
    <Form.Item name={field} noStyle>
      <RemoteSelect
        className="w-full"
        placeholder="Select..."
        initialOptions={initialOptions}
        fetchOptions={fetchOptions}
      />
    </Form.Item>
  );
}

function PlanFields() {
  return (
    <>
      <Form.Item name="l_id" label="Plan ID">
        <Input type="number" />
      </Form.Item>
      <Form.Item label="Parent">
        <PayerSelect field="l_parent_id" payerType="parent" />
      </Form.Item>
      <Form.Item label="Formulary">
        <PayerSelect field="l_formulary_id" payerType="formulary" />
      </Form.Item>
      <Form.Item name="l_mco_id" label="MCO">
        <PayerSelect field="l_mco_id" payerType="mco" />
      </Form.Item>
      <Form.Item name="l_bm_id" label="Benefit Manager">
        <PayerSelect field="l_bm_id" payerType="bm" />
      </Form.Item>
      <Form.Item name="medical_lives" label="Medical Lives">
        <Input type="number" disabled />
      </Form.Item>
      <Form.Item name="pharmacy_lives" label="Pharmacy Lives">
        <Input type="number" disabled />
      </Form.Item>
      <Form.Item name="is_national" label="Is National">
        <Select options={NationalOptions} disabled />
      </Form.Item>
      <Form.Item name="channel" label="Channel">
        <Select mode="multiple" options={channelOptions} disabled />
      </Form.Item>
      <Form.Item name="type" label="Type">
        <Select mode="multiple" options={planTypeOptions} disabled />
      </Form.Item>
      <Form.Item name="pharmacy_states" label="Pharmacy States">
        <Select mode="multiple" options={regionOptions} disabled />
      </Form.Item>
      <Form.Item name="medical_states" className="pb-6" label="Medical States">
        <Select mode="multiple" options={regionOptions} disabled />
      </Form.Item>
    </>
  );
}

function FormularyFields() {
  return (
    <>
      <Form.Item name="l_id" label="Formulary ID">
        <Input type="number" />
      </Form.Item>
      <Form.Item label="Pharmacy UM Package">
        <PayerSelect field="l_pharmacy_ump_id" payerType="ump" />
      </Form.Item>
      <Form.Item label="Medical UM Package">
        <PayerSelect field="l_medical_ump_id" payerType="ump" />
      </Form.Item>
    </>
  );
}

function UMPFields() {
  return (
    <>
      <Form.Item name="l_id" label="UMP ID">
        <Input type="number" />
      </Form.Item>
      <Form.Item name="benefit" label="Benefit">
        <Select
          options={[
            { label: 'Pharmacy', value: 'PHARMACY' },
            { label: 'Medical', value: 'MEDICAL' },
          ]}
        />
      </Form.Item>
    </>
  );
}

function BMFields() {
  return (
    <>
      <Form.Item name="l_id" label="Benefit Manager ID">
        <Input type="number" />
      </Form.Item>
      <Form.Item name="type" label="Type">
        <Select
          options={[
            { label: 'Custom', value: 'CUSTOM' },
            { label: 'National', value: 'NATIONAL' },
            { label: 'Processor', value: 'PROCESSOR' },
          ]}
        />
      </Form.Item>
      <Form.Item name="control" label="Control">
        <Select
          options={[
            { label: 'Claims', value: 'CLAIMS' },
            { label: 'Controlled', value: 'CONTROLLED' },
            { label: 'MA', value: 'MA' },
            { label: 'MAC', value: 'MAC' },
          ]}
        />
      </Form.Item>
    </>
  );
}

function MCOFields() {
  return (
    <>
      <Form.Item name="l_id" label="MCO ID">
        <Input type="number" />
      </Form.Item>
    </>
  );
}

function ParentFields() {
  return (
    <>
      <Form.Item name="l_id" label="Parent ID">
        <Input type="number" />
      </Form.Item>
    </>
  );
}

export function PayerBackboneForm(props: {
  onFinish: (p: Partial<PayerBackbone>) => Promise<void>;
  initialValues?: PayerBackbone;
  form: FormInstance;
}) {
  const { payerType } = useParams();
  if (!payerType) return null;

  return (
    <Form
      className="w-96"
      layout="vertical"
      form={props.form}
      onFinish={props.onFinish}
      initialValues={props.initialValues}
    >
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>
      {payerType === 'plan' ? (
        <PlanFields />
      ) : payerType === 'formulary' ? (
        <FormularyFields />
      ) : payerType === 'ump' ? (
        <UMPFields />
      ) : payerType === 'bm' ? (
        <BMFields />
      ) : payerType === 'mco' ? (
        <MCOFields />
      ) : payerType === 'parent' ? (
        <ParentFields />
      ) : null}
    </Form>
  );
}

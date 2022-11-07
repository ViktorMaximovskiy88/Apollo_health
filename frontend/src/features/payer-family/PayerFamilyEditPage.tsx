import { Checkbox, Form, Input } from 'antd';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MainLayout } from '../../components';
import { PayerEditSubmitComponent } from './PayerEditSubmitComponent';
import {
  useGetPayerFamilyQuery,
  useLazyGetPayerFamilyByNameQuery,
  useUpdatePayerFamilyMutation,
} from './payerFamilyApi';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { PayerFamily } from './types';

export const PayerFamilyEditPage = () => {
  const params = useParams();
  const payerFamilyId = params.payerFamilyId;

  const [form] = useForm();
  const navigate = useNavigate();
  const { data: payerFamily } = useGetPayerFamilyQuery(payerFamilyId);
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();

  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();
  const [checked, setChecked] = useState<boolean>(false);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      await updatePayerFamily({ ...values, _id: payerFamilyId }).unwrap();
      form.resetFields();
      navigate('/payer-family');
    },
    [updatePayerFamily, form, payerFamilyId, navigate]
  );

  if (!payerFamilyId || !payerFamily) {
    return <></>;
  }

  return (
    <MainLayout sectionToolbar={<PayerEditSubmitComponent form={form} />}>
      <div className="flex ml-5 space-x-4 overflow-auto flex-grow">
        <Form
          form={form}
          layout="vertical"
          disabled={isLoading}
          autoComplete="off"
          requiredMark={false}
          validateTrigger={['onBlur']}
          onFinish={onFinish}
          initialValues={payerFamily}
        >
          <Form.Item
            label="Name"
            name="name"
            className="w-96"
            rules={[
              { required: true, message: 'Please input a payer family name' },
              mustBeUnique(getPayerFamilyByName, payerFamilyId),
            ]}
          >
            <Input disabled={checked === false ? false : true} />
          </Form.Item>
          <Input.Group className="space-x-2 flex"></Input.Group>
          {form.getFieldValue('custom_name') ? 'Custom name will be generated on submission' : ''}
          <Input.Group className="space-x-2 flex">
            <Form.Item valuePropName="checked" name="custom_name">
              <Checkbox onChange={() => setChecked(!checked)}>Auto Generate</Checkbox>
            </Form.Item>
          </Input.Group>
          <PayerFamilyInfoForm />
        </Form>
        <div className="w-1/2 h-full overflow-auto"></div>
        <div className="w-1/2 h-full overflow-auto ant-tabs-h-full"></div>
      </div>
    </MainLayout>
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

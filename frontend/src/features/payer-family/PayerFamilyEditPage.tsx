import { Form, Input } from 'antd';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
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
              mustBeUniqueName(getPayerFamilyByName, payerFamily.name),
            ]}
          >
            <Input />
          </Form.Item>
          <Input.Group className="space-x-2 flex"></Input.Group>
          <PayerFamilyInfoForm />
        </Form>
      </div>
    </MainLayout>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
export function mustBeUniqueName(asyncValidator: Function, name: string) {
  return {
    async validator(_rule: Rule, value: string) {
      if (value === name) {
        return Promise.resolve();
      }
      const { data: payerFamily } = await asyncValidator({ name: value });
      if (payerFamily) {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}

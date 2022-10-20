import { Form, Input } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MainLayout } from '../../components';
import { PayerEditSubmitComponent } from './PayerEditSubmitComponent';
import { useLazyGetPayerFamilyQuery, useUpdatePayerFamilyMutation } from './payerFamilyApi';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { PayerFamily } from './types';

export const PayerFamilyEditPage = () => {
  const params = useParams();
  const payerFamilyId = params.payerFamilyId;

  const [form] = useForm();
  const navigate = useNavigate();
  const [getPayerFamily] = useLazyGetPayerFamilyQuery();
  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();

  useEffect(() => {
    const fetchCurrentPayerFamilyVals = async () => {
      const { data } = await getPayerFamily(payerFamilyId);
      if (data) {
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
  }, [form, getPayerFamily, payerFamilyId]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      await updatePayerFamily({ ...values, _id: payerFamilyId }).unwrap();
      form.resetFields();
      navigate('/payer-family');
    },
    [updatePayerFamily, form, payerFamilyId, navigate]
  );

  if (!payerFamilyId) {
    return <></>;
  }

  return (
    <MainLayout sectionToolbar={<PayerEditSubmitComponent form={form} />}>
      <div className="flex space-x-4 overflow-auto flex-grow">
        <Form
          form={form}
          layout="vertical"
          disabled={isLoading}
          autoComplete="off"
          requiredMark={false}
          validateTrigger={['onBlur']}
          onFinish={onFinish}
        >
          <div className="flex"></div>
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please input a payer family name' }]}
          >
            <Input />
          </Form.Item>
          <Input.Group className="space-x-2 flex"></Input.Group>

          <PayerFamilyInfoForm />
        </Form>
        <div className="w-1/2 h-full overflow-auto"></div>
        <div className="w-1/2 h-full overflow-auto ant-tabs-h-full"></div>
      </div>
    </MainLayout>
  );
};

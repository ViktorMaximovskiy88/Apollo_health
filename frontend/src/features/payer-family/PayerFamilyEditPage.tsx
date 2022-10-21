import { Form, Input } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect, useState } from 'react';
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
  const [initialPayerOptions, setInitialPayerOptions] = useState<any>([]);

  useEffect(() => {
    const fetchCurrentPayerFamilyVals = async () => {
      const { data } = await getPayerFamily(payerFamilyId);
      if (data) {
        //conditional used to address: Warning: Instance created by `useForm` is not connected to any Form element. Forget to pass `form` prop?
        form.setFieldsValue({
          name: data?.name,
          payer_type: data.payer_type,
          channels: data.channels,
          benefits: data.benefits,
          plan_types: data.plan_types,
          regions: data.regions,
        });
        setInitialPayerOptions(data.payer_ids);
      }
    };
    fetchCurrentPayerFamilyVals();
  }, [form, getPayerFamily, payerFamilyId]);

  console.log(form.getFieldsValue(true));

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
      <div className="flex ml-5 space-x-4 overflow-auto flex-grow">
        <Form
          form={form}
          layout="vertical"
          disabled={isLoading}
          autoComplete="off"
          requiredMark={false}
          validateTrigger={['onBlur']}
          onFinish={onFinish}
        >
          <Form.Item
            label="Name"
            name="name"
            className="w-96"
            rules={[{ required: true, message: 'Please input a payer family name' }]}
          >
            <Input />
          </Form.Item>
          <Input.Group className="space-x-2 flex"></Input.Group>
          <div className="flex"></div>
          <PayerFamilyInfoForm initialPayerOptions={initialPayerOptions} />
        </Form>
        <div className="w-1/2 h-full overflow-auto"></div>
        <div className="w-1/2 h-full overflow-auto ant-tabs-h-full"></div>
      </div>
    </MainLayout>
  );
};

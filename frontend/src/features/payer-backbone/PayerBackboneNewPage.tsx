import { Button } from 'antd';
import { FormInstance, useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../components';
import { useAddPayerBackboneMutation } from './payerBackboneApi';
import { PayerBackboneForm } from './PayerBackboneForm';
import { PayerBackboneSubMenu } from './PayerBackboneSubMenu';
import { PayerBackbone } from './types';

export function SumbitPayerBackbone({ form }: { form: FormInstance<any> }) {
  const { payerType } = useParams();
  const navigate = useNavigate();
  return (
    <div className="flex items-center space-x-4">
      <Button
        onClick={() => {
          navigate(`../${payerType}`);
        }}
      >
        Cancel
      </Button>
      <Button
        type="primary"
        onClick={() => {
          form.submit();
        }}
      >
        Submit
      </Button>
    </div>
  );
}
export function PayerBackboneNewPage() {
  const [form] = useForm();
  const navigate = useNavigate();
  const { payerType } = useParams();

  const [create] = useAddPayerBackboneMutation();
  const onFinish = useCallback(
    async (body: Partial<PayerBackbone>) => {
      await create({ payerType, body });
      navigate('..');
    },
    [navigate, payerType, create]
  );
  return (
    <MainLayout
      sidebar={<PayerBackboneSubMenu />}
      sectionToolbar={<SumbitPayerBackbone form={form} />}
    >
      <div className="flex h-full">
        <PayerBackboneForm form={form} onFinish={onFinish} />
      </div>
    </MainLayout>
  );
}

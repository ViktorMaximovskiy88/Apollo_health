import { useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../components';
import { useGetPayerBackboneQuery, useUpdatePayerBackboneMutation } from './payerBackboneApi';
import { PayerBackboneForm } from './PayerBackboneForm';
import { SumbitPayerBackbone } from './PayerBackboneNewPage';
import { PayerBackboneSubMenu } from './PayerBackboneSubMenu';
import { PayerBackbone } from './types';

export function PayerBackboneEditPage() {
  const [form] = useForm();
  const navigate = useNavigate();

  const { payerType, payerId } = useParams();
  const { data } = useGetPayerBackboneQuery({ id: payerId, payerType });

  const [update] = useUpdatePayerBackboneMutation();
  const onFinish = useCallback(
    async (res: Partial<PayerBackbone>) => {
      await update({ body: { ...res, _id: payerId }, payerType });
      navigate('..');
    },
    [navigate, update, payerId, payerType]
  );

  return (
    <MainLayout
      sidebar={<PayerBackboneSubMenu />}
      sectionToolbar={<SumbitPayerBackbone form={form} />}
    >
      <div className="flex h-full">
        {data && <PayerBackboneForm initialValues={data} form={form} onFinish={onFinish} />}
      </div>
    </MainLayout>
  );
}

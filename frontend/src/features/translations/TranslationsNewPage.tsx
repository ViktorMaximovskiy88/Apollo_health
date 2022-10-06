import { Button } from 'antd';
import { FormInstance, useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../../components';
import { useAddTranslationConfigMutation } from './translationApi';
import { TranslationDocPreview } from './TranslationDocPreview';
import { TranslationForm } from './TranslationForm';
import { TranslationConfig } from './types';

function SumbitTranslation({ form }: { form: FormInstance<any> }) {
  const navigate = useNavigate();
  return (
    <div className="flex items-center space-x-4">
      <Button
        onClick={() => {
          navigate('..');
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
export function TranslationsNewPage() {
  const [form] = useForm();
  const navigate = useNavigate();
  const [create] = useAddTranslationConfigMutation();
  const onFinish = useCallback(
    async (res: Partial<TranslationConfig>) => {
      await create(res);
      navigate('..');
    },
    [navigate, create]
  );
  return (
    <MainLayout sectionToolbar={<SumbitTranslation form={form} />}>
      <div className="flex h-full">
        <div className="w-1/2 h-full">
          <TranslationForm form={form} onFinish={onFinish} />
        </div>
        <div className="w-1/2 h-full">
          <TranslationDocPreview form={form} />
        </div>
      </div>
    </MainLayout>
  );
}

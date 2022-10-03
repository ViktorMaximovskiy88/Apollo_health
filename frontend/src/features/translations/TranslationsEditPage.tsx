import { Button } from 'antd';
import { FormInstance, useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../components';
import { useGetTranslationConfigQuery, useUpdateTranslationConfigMutation } from './translationApi';
import { TranslationDocPreview } from './TranslationDocPreview';
import { TranslationForm } from './TranslationForm';
import { TranslationConfig } from './types';

function SaveAs({ form }: { form: FormInstance<any> }) {
  return (
    <Button
      style={{ color: 'white', backgroundColor: '#6C757D' }} // TODO: refactor to use type prop or classname
    >
      Save As
    </Button>
  );
}

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
      <SaveAs form={form} />
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
export function TranslationsEditPage() {
  const [form] = useForm();
  const navigate = useNavigate();
  const [update] = useUpdateTranslationConfigMutation();
  const { translationId } = useParams();
  const { data: config } = useGetTranslationConfigQuery(translationId);
  const onFinish = useCallback(
    async (res: Partial<TranslationConfig>) => {
      await update({ _id: translationId, ...res });
      navigate('..');
    },
    [translationId, navigate, update]
  );

  if (!config) return null;

  return (
    <MainLayout pageTitle={'Translations'} sectionToolbar={<SumbitTranslation form={form} />}>
      <div className="flex h-full">
        <div className="w-1/2 h-full">
          <TranslationForm form={form} initialValues={config} onFinish={onFinish} />
        </div>
        <div className="w-1/2 h-full">
          <TranslationDocPreview form={form} />
        </div>
      </div>
    </MainLayout>
  );
}

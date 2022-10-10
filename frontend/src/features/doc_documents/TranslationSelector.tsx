import { Form, Button, ModalProps, Modal } from 'antd';
import { useCallback, useState, useMemo, useEffect } from 'react';
import tw from 'twin.macro';
import { RemoteSelect } from '../../components/RemoteSelect';
import {
  useLazyGetTranslationConfigsQuery,
  useGetTranslationConfigQuery,
} from '../translations/translationApi';
import { TranslationDocPreview } from '../translations/TranslationDocPreview';
import { TranslationForm } from '../translations/TranslationForm';
import { TranslationConfig } from '../translations/types';
import { useGetDocDocumentQuery } from './docDocumentApi';

function TranslationSelector({ translation }: { translation?: TranslationConfig }) {
  const [getTranslations] = useLazyGetTranslationConfigsQuery();
  const initialOptions = translation ? [{ value: translation._id, label: translation.name }] : [];
  const translationOptions = useCallback(
    async (search: string) => {
      const { data } = await getTranslations({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((site) => ({ label: site.name, value: site._id }));
    },
    [getTranslations]
  );
  return (
    <Form.Item className="grow" name="translation_id" label="Translation">
      <RemoteSelect
        allowClear
        className="w-full"
        initialOptions={initialOptions}
        fetchOptions={translationOptions}
      />
    </Form.Item>
  );
}

export function Translation() {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);

  const translationId = Form.useWatch('translation_id');
  const { data: translation } = useGetTranslationConfigQuery(translationId, {
    skip: !translationId,
  });

  if (!doc) return null;

  // need any siteId for 'testing', grab the first (every doc has one at least)
  const siteId = doc.locations[0].site_id;

  return (
    <div className="flex">
      <TranslationSelector translation={translation} />
      <TranslationModal translation={translation} siteId={siteId} docId={doc._id} />
    </div>
  );
}

function TranslationModal({
  translation,
  siteId,
  docId,
}: {
  translation?: TranslationConfig;
  siteId: string;
  docId: string;
}) {
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [form] = Form.useForm();

  const initialValues = useMemo(() => {
    const sample = { site_id: siteId, doc_id: docId };
    return translation ? { ...translation, sample } : undefined;
  }, [translation, siteId, docId]);

  useEffect(() => {
    if (testModalOpen) {
      form.setFieldsValue(initialValues);
    }
  }, [initialValues, testModalOpen, form]);

  return (
    <Form.Item label=" ">
      {translation && (
        <>
          <Button onClick={() => setTestModalOpen(true)} type="link">
            Test
          </Button>
          <FullScreenModal
            open={testModalOpen}
            onCancel={() => setTestModalOpen(false)}
            onOk={() => setTestModalOpen(false)}
          >
            <div className="flex h-full">
              <div className="w-1/2 h-full">
                <TranslationForm form={form} initialValues={initialValues} onFinish={() => {}} />
              </div>
              <div className="w-1/2 h-full">
                <TranslationDocPreview form={form} />
              </div>
            </div>
          </FullScreenModal>
        </>
      )}
    </Form.Item>
  );
}

function FullScreenModal({ children, ...props }: ModalProps) {
  return (
    <Modal
      width={'97vw'}
      className="p-0 ant-modal-full-screen"
      style={{ top: '3vh', height: '94vh' }}
      bodyStyle={tw`h-full overflow-auto`}
      {...props}
    >
      {children}
    </Modal>
  );
}

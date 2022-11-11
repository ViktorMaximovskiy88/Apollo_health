import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../../components';
import { Form, Input, Select, Typography } from 'antd';
import {
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamilyByNameQuery,
  useUpdateDocumentFamilyMutation,
} from './documentFamilyApi';
import { SubmitDocumentFamily } from './SubmitDocumentFamily';
import { DocumentFamily } from './types';
import { DocumentTypes } from '../../retrieved_documents/types';
import { useNotifyMutation } from '../../../common/hooks';

import { fieldGroupsOptions, legacyRelevanceOptions } from './documentFamilyLevels';
import { filterLegacyRelevanceOptions, mustBeUniqueName } from './DocumentFamilyCreateDrawer';

export function DocumentFamilyEditPage() {
  const [form] = useForm();
  const navigate = useNavigate();

  const { documentFamilyId } = useParams();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const { data } = useGetDocumentFamilyQuery(documentFamilyId);
  const original = data?.name;
  const [update, result] = useUpdateDocumentFamilyMutation();
  const nameValue: string[] = Form.useWatch('legacy_relevance', form);
  let filteredlegacyRelevanceOptions = legacyRelevanceOptions;

  filteredlegacyRelevanceOptions = filterLegacyRelevanceOptions(legacyRelevanceOptions, nameValue);

  useNotifyMutation(
    result,
    { description: 'Document Family Updated Successfully.' },
    { description: 'An error occurred while updating the Document Family.' }
  );

  useEffect(() => {
    if (result.isSuccess || result.isError) navigate('..');
  }, [result.isSuccess, result.isError, navigate]);

  const onFinish = useCallback(
    async (res: Partial<DocumentFamily>) => {
      await update({ body: res, _id: documentFamilyId });
    },
    [update, documentFamilyId]
  );

  return (
    <MainLayout sectionToolbar={<SubmitDocumentFamily form={form} />}>
      <div>
        {data && (
          <Form
            form={form}
            layout="vertical"
            autoComplete="off"
            requiredMark={false}
            validateTrigger={['onBlur']}
            onFinish={onFinish}
            initialValues={data}
          >
            <div className="flex">
              <div className="flex-1 mt-2 mb-4">
                <Typography.Title level={3}>Document Family Information</Typography.Title>
              </div>
            </div>
            <Input.Group className="flex grow space-x-3">
              <Form.Item
                label="Name"
                name="name"
                className="w-1/2"
                rules={[
                  { required: true, message: 'Please input a document family name' },
                  mustBeUniqueName(getDocumentFamilyByName, original),
                ]}
              >
                <Input />
              </Form.Item>
              <Form.Item
                label="Document Type"
                name="document_type"
                className="w-1/2"
                rules={[{ required: true, message: 'Please input a Document Type' }]}
              >
                <Select showSearch options={DocumentTypes} />
              </Form.Item>
            </Input.Group>

            <Input.Group className="flex grow space-x-3">
              <Form.Item
                label="Legacy Relevance"
                name="legacy_relevance"
                className="w-1/2"
                rules={[{ required: true, message: 'Please input a legacy relevance' }]}
              >
                <Select mode="multiple" options={filteredlegacyRelevanceOptions} />
              </Form.Item>

              <Form.Item label="Field Groups" name="field_groups" className="w-1/2">
                <Select mode="multiple" options={fieldGroupsOptions} />
              </Form.Item>
            </Input.Group>
          </Form>
        )}
      </div>
    </MainLayout>
  );
}

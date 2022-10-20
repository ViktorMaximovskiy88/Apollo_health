import { useForm } from 'antd/lib/form/Form';
import { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../../components';
import { Rule } from 'antd/lib/form';
import { Form, Input, Select } from 'antd';
import {
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamilyByNameQuery,
  useUpdateDocumentFamilyMutation,
} from './documentFamilyApi';
import { SumbitDocumentFamily } from './SumbitDocumentFamily';
import { DocumentFamily } from './types';
import { DocumentTypes } from '../../retrieved_documents/types';

import { fieldGroupsOptions, legacyRelevanceOptions } from './documentFamilyLevels';
import { mustBeUniqueName } from './DocumentFamilyCreateModal';

export function DocumentFamilyEditPage() {
  const [form] = useForm();
  const navigate = useNavigate();

  const { documentFamilyId } = useParams();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const { data } = useGetDocumentFamilyQuery(documentFamilyId);
  const original = data?.name;
  const [update] = useUpdateDocumentFamilyMutation();
  const nameValue: string[] = Form.useWatch('legacy_relevance', form);
  let filteredlegacyRelevanceOptions = legacyRelevanceOptions;

  if (nameValue?.includes('N/A')) {
    filteredlegacyRelevanceOptions = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') return e;
      return { ...e, disabled: true };
    });
  } else if (
    nameValue?.includes('PAR') ||
    nameValue?.includes('EDITOR_MANUAL') ||
    nameValue?.includes('EDITOR_AUTOMATED')
  ) {
    filteredlegacyRelevanceOptions = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') {
        return { ...e, disabled: true };
      } else if (
        (nameValue?.includes('EDITOR_MANUAL') && e.value == 'EDITOR_AUTOMATED') ||
        (nameValue?.includes('EDITOR_AUTOMATED') && e.value == 'EDITOR_MANUAL')
      ) {
        return { ...e, disabled: true };
      }
      return e;
    });
  }

  const onFinish = useCallback(
    async (res: Partial<DocumentFamily>) => {
      await update({ body: res, _id: documentFamilyId });
      navigate('..');
    },
    [navigate, update, documentFamilyId]
  );

  return (
    <MainLayout sectionToolbar={<SumbitDocumentFamily form={form} />}>
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
                <h3>Edit Document Family</h3>
                <div>{data.document_type}</div>
              </div>
            </div>
            <Input.Group className="flex grow space-x-3">
              <Form.Item
                label="Document Family Name"
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
                <Select options={DocumentTypes} />
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

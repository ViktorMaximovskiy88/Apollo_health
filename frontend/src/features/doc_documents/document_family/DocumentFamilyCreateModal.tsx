import { Button, Drawer, Form, Input, Select } from 'antd';
import {
  useLazyGetDocumentFamilyByNameQuery,
  useAddDocumentFamilyMutation,
  useUpdateDocumentFamilyMutation,
} from './documentFamilyApi';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useEffect } from 'react';
import { fieldGroupsOptions, legacyRelevanceOptions } from './documentFamilyLevels';
import { DocumentFamily } from './types';
import { CloseOutlined } from '@ant-design/icons';

interface DocumentFamilyCreateModalPropTypes {
  documentType?: string;
  open?: boolean;
  onClose: () => void;
  onSave: (documentFamilyId: string) => void;
  documentFamilyData?: DocumentFamily;
}

export const DocumentFamilyCreateModal = (props: DocumentFamilyCreateModalPropTypes) => {
  const { documentType, open, documentFamilyData, onClose, onSave } = props;
  const [form] = useForm();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const [addDocumentFamily, { isLoading, data, isSuccess, reset }] = useAddDocumentFamilyMutation();
  const [update, { isLoading: isUpdateLoading, data: updateData, isSuccess: isUpdateSuccess }] =
    useUpdateDocumentFamilyMutation();
  const nameValue: string[] = Form.useWatch('legacy_relevance', form);
  let filteredlegacyRelevanceOptions = legacyRelevanceOptions;

  filteredlegacyRelevanceOptions = filterLegacyRelevanceOptions(legacyRelevanceOptions, nameValue);

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data._id);
      form.resetFields();
      reset();
    }
  }, [isSuccess, data, onSave, form]);

  useEffect(() => {
    if (isUpdateSuccess && updateData) {
      onSave(updateData._id);
      form.resetFields();
    }
  }, [isUpdateSuccess, updateData]);

  useEffect(() => {
    form.setFieldsValue(documentFamilyData);
  }, [documentFamilyData]);
  return (
    <Drawer
      open={open}
      title={documentFamilyData ? <>Edit Document Family</> : <>Add Document Family</>}
      width="20%"
      placement="left"
      closable={false}
      mask={false}
      extra={
        <Button type="text" onClick={onClose}>
          <CloseOutlined />
        </Button>
      }
    >
      <Form
        form={form}
        layout="vertical"
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={(values: any) => {
          if (documentFamilyData) {
            update({ body: values, _id: documentFamilyData._id });
            form.resetFields();
          } else {
            addDocumentFamily({
              ...values,
              document_type: documentType,
            });
          }
        }}
      >
        <div className="flex">
          <div className="flex-1 mt-2 mb-4">
            <h3>Document Type</h3>
            <div>{documentType}</div>
          </div>
        </div>
        <Form.Item
          label="Name"
          name="name"
          rules={[
            { required: true, message: 'Please input a document family name' },
            mustBeUniqueName(getDocumentFamilyByName, documentFamilyData?.name),
          ]}
        >
          <Input />
        </Form.Item>
        <Input.Group className="space-x-2 flex">
          <Form.Item
            label="Legacy Relevance"
            name="legacy_relevance"
            className="w-full"
            rules={[{ required: true, message: 'Please input a legacy relevance' }]}
          >
            <Select mode="multiple" options={filteredlegacyRelevanceOptions} />
          </Form.Item>

          <Form.Item label="Field Groups" name="field_groups" className="w-full">
            <Select mode="multiple" options={fieldGroupsOptions} />
          </Form.Item>
        </Input.Group>
        <div className="space-x-2 flex justify-end">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" onClick={form.submit} loading={isLoading || isUpdateLoading}>
            Submit
          </Button>
        </div>
      </Form>
    </Drawer>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
export function mustBeUniqueName(asyncValidator: Function, name: string = '') {
  return {
    async validator(_rule: Rule, value: string) {
      if (value === name) {
        return Promise.resolve();
      }
      const { data: documentFamily } = await asyncValidator({ name: value });
      if (documentFamily) {
        return Promise.reject(`Document family name "${documentFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}

export function filterLegacyRelevanceOptions(
  legacyRelevanceOptions: { label: string; value: string }[],
  nameValue: string[]
) {
  let filtered = legacyRelevanceOptions;
  if (nameValue?.includes('N/A')) {
    filtered = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') return e;
      return { ...e, disabled: true };
    });
  } else if (
    nameValue?.includes('PAR') ||
    nameValue?.includes('EDITOR_MANUAL') ||
    nameValue?.includes('EDITOR_AUTOMATED')
  ) {
    filtered = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') {
        return { ...e, disabled: true };
      } else if (
        (nameValue?.includes('EDITOR_MANUAL') && e.value === 'EDITOR_AUTOMATED') ||
        (nameValue?.includes('EDITOR_AUTOMATED') && e.value === 'EDITOR_MANUAL')
      ) {
        return { ...e, disabled: true };
      }
      return e;
    });
  }
  return filtered;
}

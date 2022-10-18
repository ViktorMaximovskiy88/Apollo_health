import { Form, Input, Select } from 'antd';
import {
  useLazyGetDocumentFamilyByNameQuery,
  useAddDocumentFamilyMutation,
} from './documentFamilyApi';
import { DocDocumentLocation } from '../locations/types';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useEffect } from 'react';
import { fieldGroupsOptions, legacyRelevanceOptions } from './documentFamilyLevels';

interface DocumentFamilyCreateModalPropTypes {
  documentType?: string;
  open?: boolean;
  onClose: () => void;
  onSave: (documentFamilyId: string) => void;
}

export const DocumentFamilyCreateModal = (props: DocumentFamilyCreateModalPropTypes) => {
  const { documentType, open, onClose, onSave } = props;
  const [form] = useForm();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const [addDocumentFamily, { isLoading, data, isSuccess }] = useAddDocumentFamilyMutation();
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

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data._id);
      form.resetFields();
    }
  }, [isSuccess, data]);

  return (
    <Modal
      open={open}
      title={<>Add Document Family</>}
      width="50%"
      okText="Submit"
      onOk={form.submit}
      onCancel={onClose}
    >
      <Form
        form={form}
        layout="vertical"
        disabled={isLoading}
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={(values: any) => {
          addDocumentFamily({
            ...values,
            document_type: documentType,
          });
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
            mustBeUniqueName(getDocumentFamilyByName),
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
      </Form>
    </Modal>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
function mustBeUniqueName(asyncValidator: Function) {
  return {
    async validator(_rule: Rule, value: string) {
      const { data: documentFamily } = await asyncValidator({ name: value });
      if (documentFamily) {
        return Promise.reject(`Document family name "${documentFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}

import { Button, Drawer, Form, Input, Select } from 'antd';
import {
  useLazyGetDocumentFamilyByNameQuery,
  useAddDocumentFamilyMutation,
  useUpdateDocumentFamilyMutation,
} from './documentFamilyApi';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useEffect } from 'react';
import { LegacyRelevanceOptions } from './documentFamilyLevels';
import { FieldGroupsOptions } from './documentFamilyLevels';
import { DocumentFamily } from './types';
import { CloseOutlined } from '@ant-design/icons';
import { DocumentTypes } from '../../retrieved_documents/types';

const DocumentType = (props: { documentType?: string }) => (
  <>
    {props.documentType ? (
      <div className="flex">
        <div className="flex-1 mt-2 mb-4">
          <h3>Document Type</h3>
          <div>{props.documentType}</div>
        </div>
      </div>
    ) : (
      <Form.Item
        label="Document Type"
        name="document_type"
        rules={[{ required: true, message: 'Please input a document type.' }]}
      >
        <Select showSearch options={DocumentTypes} />
      </Form.Item>
    )}
  </>
);

interface DocumentFamilyCreateDrawerPropTypes {
  documentType?: string;
  open?: boolean;
  onClose: () => void;
  documentFamilyData?: DocumentFamily;
  onSave: (documentFamily: DocumentFamily) => void;
  mask?: boolean;
}

export const DocumentFamilyCreateDrawer = (props: DocumentFamilyCreateDrawerPropTypes) => {
  const { open, documentFamilyData, onClose, onSave, mask = true } = props;
  const [form] = useForm();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const [addDocumentFamily, { isLoading, data, isSuccess, reset }] = useAddDocumentFamilyMutation();
  const [update, { isLoading: isUpdateLoading, data: updateData, isSuccess: isUpdateSuccess }] =
    useUpdateDocumentFamilyMutation();
  const nameValue: string[] = Form.useWatch('legacy_relevance', form);
  let filteredlegacyRelevanceOptions = LegacyRelevanceOptions;

  filteredlegacyRelevanceOptions = filterLegacyRelevanceOptions(LegacyRelevanceOptions, nameValue);

  const handleClose = () => {
    onClose();
  };

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data);
      form.resetFields();
      reset();
    }
  }, [isSuccess, data, onSave, form]);

  useEffect(() => {
    if (isUpdateSuccess && updateData) {
      onSave(updateData);
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
      width="30%"
      placement="left"
      closable={false}
      mask={mask}
      extra={
        <Button type="text" onClick={handleClose}>
          <CloseOutlined />
        </Button>
      }
      onClose={handleClose}
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
          } else if (props.documentType) {
            addDocumentFamily({
              ...values,
              document_type: props.documentType,
            });
          } else {
            addDocumentFamily({ ...values });
          }
        }}
      >
        <DocumentType documentType={props.documentType} />
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
            <Select mode="multiple" options={FieldGroupsOptions} />
          </Form.Item>
        </Input.Group>
        <div className="space-x-2 flex justify-end">
          <Button onClick={handleClose}>Cancel</Button>
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
      if (!value) {
        return Promise.reject();
      }
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
  legacyRelevanceOptions: { label: string; value: string; id: string }[],
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

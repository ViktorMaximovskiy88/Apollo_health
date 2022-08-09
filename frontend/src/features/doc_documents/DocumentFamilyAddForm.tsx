import { Form, Modal, Spin, Button, FormInstance } from 'antd';
import { DocumentFamilyOption, DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { ThresholdFields, initialThresholdValues } from './DocumentFamilyThresholdFields';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useState } from 'react';

const useAddDocumentFamily = () => {
  const [addDocumentFamilyFn] = useAddDocumentFamilyMutation();

  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);

  async function addDocumentFamily(documentFamily: DocumentFamilyType): Promise<string> {
    if (!doc) {
      throw new Error('DocDocument not found');
    }

    documentFamily.sites = [doc.site_id];
    documentFamily.document_type = documentType;

    const { _id } = await addDocumentFamilyFn(documentFamily).unwrap();
    return _id;
  }

  return addDocumentFamily;
};

const saveInMultiselect = (docDocumentForm: FormInstance, documentFamilyId: string): void => {
  const selected = docDocumentForm.getFieldValue('document_families');
  docDocumentForm.setFieldsValue({
    document_families: [...selected, documentFamilyId],
  });
};

const DocumentType = ({ docDocumentForm }: { docDocumentForm: FormInstance }) => {
  const documentType = docDocumentForm.getFieldValue('document_type');
  return (
    <Form.Item label="Document Type" className="flex-1">
      <b>{documentType}</b>
    </Form.Item>
  );
};
const SiteName = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const { data: site } = useGetSiteQuery(doc?.site_id);

  if (!site) return null;

  return (
    <Form.Item label="Site Name" className="flex-1">
      {site?.name ? <b>{site.name}</b> : <Spin size="small" />}
    </Form.Item>
  );
};

const Footer = ({ onCancel, isLoading }: { onCancel: () => void; isLoading: boolean }) => (
  <div className="ant-modal-footer mt-3">
    <Button onClick={onCancel}>Cancel</Button>
    <Button type="primary" htmlType="submit" loading={isLoading}>
      Submit
    </Button>
  </div>
);

interface AddDocumentFamilyPropTypes {
  options: DocumentFamilyOption[];
  setOptions: (options: DocumentFamilyOption[]) => void;
  closeModal: () => void;
  visible: boolean;
}
export function AddDocumentFamily({
  options,
  setOptions,
  closeModal,
  visible,
}: AddDocumentFamilyPropTypes) {
  const [isLoading, setIsLoading] = useState(false);
  const docDocumentForm = Form.useFormInstance();
  const [documentFamilyForm] = Form.useForm();
  const addDocumentFamily = useAddDocumentFamily();

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    setIsLoading(true);
    const documentFamilyId = await addDocumentFamily(documentFamily);
    saveInMultiselect(docDocumentForm, documentFamilyId);

    setOptions([...options, { value: documentFamilyId, label: documentFamily.name }]);

    documentFamilyForm.resetFields();
    closeModal();
    setIsLoading(false);
  };

  const onCancel = () => {
    documentFamilyForm.resetFields();
    closeModal();
  };

  return (
    <Modal
      visible={visible}
      onCancel={closeModal}
      title="Add Document Family"
      width="50%"
      okText="Submit"
      footer={null}
    >
      <Form
        onFinish={onFinish}
        initialValues={initialThresholdValues}
        form={documentFamilyForm}
        name="add-document-family"
        layout="vertical"
        className="h-full"
        autoComplete="off"
      >
        <Name />
        <div className="flex space-x-8">
          <DocumentType docDocumentForm={docDocumentForm} />
          <SiteName />
        </div>
        <ThresholdFields docDocumentForm={docDocumentForm} />
        <Footer onCancel={onCancel} isLoading={isLoading} />
      </Form>
    </Modal>
  );
}

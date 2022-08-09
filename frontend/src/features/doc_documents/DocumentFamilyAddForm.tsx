import { Form, Modal, Spin, Button } from 'antd';
import { DocumentFamilyOption, DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { ThresholdFields, initialThresholdValues } from './DocumentFamilyThresholdFields';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useContext, useState } from 'react';
import { DocDocumentFormContext } from './DocumentFamilyField';

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

const useSaveInMultiselect = () => {
  const docDocumentForm = useContext(DocDocumentFormContext);

  const saveInMultiselect = (documentFamilyId: string): void => {
    const selected = docDocumentForm.getFieldValue('document_families');
    docDocumentForm.setFieldsValue({
      document_families: [...selected, documentFamilyId],
    });
  };

  return saveInMultiselect;
};

const DocumentType = () => {
  const docDocumentForm = useContext(DocDocumentFormContext);
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

const Footer = ({ onCancel, isSaving }: { onCancel: () => void; isSaving: boolean }) => (
  <div className="ant-modal-footer mt-3">
    <Button onClick={onCancel}>Cancel</Button>
    <Button type="primary" htmlType="submit" loading={isSaving}>
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
  const [isSaving, setIsSaving] = useState(false);
  const [documentFamilyForm] = Form.useForm();
  const addDocumentFamily = useAddDocumentFamily();
  const saveInMultiselect = useSaveInMultiselect();

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    setIsSaving(true);

    const documentFamilyId = await addDocumentFamily(documentFamily);
    saveInMultiselect(documentFamilyId);

    setOptions([...options, { value: documentFamilyId, label: documentFamily.name }]);

    documentFamilyForm.resetFields();
    closeModal();

    setIsSaving(false);
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
        disabled={isSaving}
      >
        <Name />
        <div className="flex space-x-8">
          <DocumentType />
          <SiteName />
        </div>
        <ThresholdFields />
        <Footer onCancel={onCancel} isSaving={isSaving} />
      </Form>
    </Modal>
  );
}

import { Form, Modal, Spin, Button } from 'antd';
import { DocumentFamilyOption, DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useContext, useState } from 'react';
import { DocDocumentFormContext } from './DocumentFamilyAddNew';

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

const useSaveInSelect = (): ((documentFamilyId: string) => void) => {
  const docDocumentForm = useContext(DocDocumentFormContext);

  const saveInSelect = (documentFamilyId: string): void => {
    docDocumentForm.setFieldsValue({
      document_family: documentFamilyId,
    });
  };

  return saveInSelect;
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
  const saveInSelect = useSaveInSelect();

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    setIsSaving(true);

    const documentFamilyId = await addDocumentFamily(documentFamily);
    saveInSelect(documentFamilyId);

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
        form={documentFamilyForm}
        name="add-document-family"
        layout="vertical"
        className="h-full"
        autoComplete="off"
        disabled={isSaving}
        validateTrigger={['onBlur']}
      >
        <Name />
        <div className="flex space-x-8">
          <DocumentType />
          <SiteName />
        </div>
        <Footer onCancel={onCancel} isSaving={isSaving} />
      </Form>
    </Modal>
  );
}

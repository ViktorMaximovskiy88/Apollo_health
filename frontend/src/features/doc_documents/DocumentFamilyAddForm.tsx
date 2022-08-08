import { Form, Modal, Spin, Button, FormInstance } from 'antd';
import { DocDocument, DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { ThresholdFields, initialThresholdValues } from './DocumentFamilyThresholdFields';

const useAddDocumentFamily = (doc: DocDocument) => {
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);

  const { data: site } = useGetSiteQuery(doc.site_id);
  const [addDocumentFamilyFn] = useAddDocumentFamilyMutation();

  async function addDocumentFamily(documentFamily: DocumentFamilyType): Promise<string> {
    documentFamily.sites = site?._id ? [site._id] : [];
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

const DocumentType = () => {
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);
  return (
    <Form.Item label="Document Type" className="flex-1">
      <b>{documentType}</b>
    </Form.Item>
  );
};
const SiteName = ({ doc }: { doc: DocDocument }) => {
  const { data: site } = useGetSiteQuery(doc.site_id);
  return (
    <Form.Item label="Site Name" className="flex-1">
      {site?.name ? <b>{site.name}</b> : <Spin size="small" />}
    </Form.Item>
  );
};

const Footer = ({ onCancel }: { onCancel: () => void }) => (
  <div className="ant-modal-footer mt-3">
    <Button onClick={onCancel}>Cancel</Button>
    <Button type="primary" htmlType="submit">
      Submit
    </Button>
  </div>
);

interface AddDocumentFamilyPropTypes {
  closeModal: () => void;
  visible: boolean;
  doc: DocDocument;
  docDocumentForm: FormInstance;
}
export function AddDocumentFamily({
  doc,
  closeModal,
  visible,
  docDocumentForm,
}: AddDocumentFamilyPropTypes) {
  const [documentFamilyForm] = Form.useForm();
  const addDocumentFamily = useAddDocumentFamily(doc);

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    const documentFamilyId = await addDocumentFamily(documentFamily);
    saveInMultiselect(docDocumentForm, documentFamilyId);

    documentFamilyForm.resetFields();
    closeModal();
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
        <div className="flex space-x-8">
          <Name />
        </div>
        <div className="flex space-x-8">
          <DocumentType />
          <SiteName doc={doc} />
        </div>
        <ThresholdFields />
        <Footer onCancel={onCancel} />
      </Form>
    </Modal>
  );
}

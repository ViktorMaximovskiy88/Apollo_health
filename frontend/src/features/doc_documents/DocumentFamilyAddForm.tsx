import { Form, Modal, InputNumber, Spin, Button, FormInstance } from 'antd';
import { DocDocument, DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Site } from '../sites/types';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';

const initialValues = {
  document_type_threshold: 75,
  therapy_tag_status_threshold: 75,
  lineage_threshold: 75,
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
const SiteName = ({ site }: { site?: Site }) => (
  <Form.Item label="Site Name" className="flex-1">
    {site?.name ? <b>{site.name}</b> : <Spin size="small" />}
  </Form.Item>
);
const DocumentTypeThreshold = () => (
  <Form.Item
    name="document_type_threshold"
    label="Document Type Confidence Threshold"
    className="flex-1"
    rules={[{ required: true, message: 'Please input a Document Type Confidence Threshold!' }]}
    required
  >
    <InputNumber min={1} max={100} addonAfter="%" />
  </Form.Item>
);
const TherapyTagStatusThreshold = () => (
  <Form.Item
    name="therapy_tag_status_threshold"
    label="Therapy Tag Confidence Threshold"
    className="flex-1"
    rules={[{ required: true, message: 'Please input a Therapy Tag Confidence Threshold!' }]}
    required
  >
    <InputNumber min={1} max={100} addonAfter="%" />
  </Form.Item>
);
const LineageThreshold = () => (
  <Form.Item
    name="lineage_threshold"
    label="Lineage Confidence Threshold"
    className="flex-1"
    rules={[{ required: true, message: 'Please input a Lineage Confidence Threshold!' }]}
    required
  >
    <InputNumber min={1} max={100} addonAfter="%" />
  </Form.Item>
);
const Footer = ({ onCancel }: { onCancel: () => void }) => (
  <div className="ant-modal-footer mt-3">
    <Button onClick={onCancel}>Cancel</Button>
    <Button type="primary" htmlType="submit">
      Submit
    </Button>
  </div>
);

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
  const { data: site } = useGetSiteQuery(doc.site_id);
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
        initialValues={initialValues}
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
          <SiteName site={site} />
        </div>
        <div className="flex space-x-8">
          <DocumentTypeThreshold />
          <TherapyTagStatusThreshold />
          <LineageThreshold />
        </div>
        <Footer onCancel={onCancel} />
      </Form>
    </Modal>
  );
}

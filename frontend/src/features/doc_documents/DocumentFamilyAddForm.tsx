import { Form, Modal, InputNumber, Spin, Button, FormInstance } from 'antd';
import { DocDocument, DocumentFamilyType, DocumentFamilyOption } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Site } from '../sites/types';
import { Name } from './DocumentFamilyNameField';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';

const initialValues = {
  document_type_threshold: 75,
  therapy_tag_status_threshold: 75,
  lineage_threshold: 75,
};

const DocumentType = ({ doc }: { doc: DocDocument }) => (
  <Form.Item label="Document Type" className="flex-1">
    <b>{doc.document_type}</b>
  </Form.Item>
);
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

interface AddDocumentFamilyPropTypes {
  closeModal: () => void;
  visible: boolean;
  doc: DocDocument;
  options: DocumentFamilyOption[];
  setOptions: (options: DocumentFamilyOption[]) => void;
  docDocumentForm: FormInstance;
}
export function AddDocumentFamily({
  doc,
  closeModal,
  visible,
  options,
  setOptions,
  docDocumentForm,
}: AddDocumentFamilyPropTypes) {
  const { data: site } = useGetSiteQuery(doc.site_id);
  const [documentFamilyForm] = Form.useForm();
  const [addDocumentFamily] = useAddDocumentFamilyMutation();

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    documentFamily.sites = site?._id ? [site._id] : [];
    documentFamily.document_type = doc.document_type;

    documentFamilyForm.resetFields();
    closeModal();

    const { _id, name } = await addDocumentFamily(documentFamily).unwrap();
    documentFamily._id = _id;

    setOptions([{ label: name, value: _id, ...documentFamily }, ...options]);

    const selected = docDocumentForm.getFieldValue('document_families');
    docDocumentForm.setFieldsValue({
      document_families: [...selected, { label: name, value: _id, ...documentFamily }],
    });
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
          <DocumentType doc={doc} />
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

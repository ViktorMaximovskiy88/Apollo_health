import { Form, Modal, InputNumber, Spin, Button } from 'antd';
import { DocDocument, DocumentFamily as DocumentFamilyType } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { Site } from '../sites/types';
import { Name } from './DocumentFamilyNameField';

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
  options: string[];
  setOptions: (options: string[]) => void;
}
export function AddDocumentFamily({
  doc,
  closeModal,
  visible,
  options,
  setOptions,
}: AddDocumentFamilyPropTypes) {
  const { data: site } = useGetSiteQuery(doc.site_id);
  const [form] = Form.useForm();

  const onFinish = (documentFamily: DocumentFamilyType) => {
    form.resetFields();
    closeModal();
    setOptions([documentFamily.name, ...options]);
  };

  const onCancel = () => {
    form.resetFields();
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
        form={form}
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

import { Form, Select, Modal, InputNumber, Spin, Button } from 'antd';
import { DocDocument } from './types';
import { useState } from 'react';
import { useGetSiteQuery } from '../sites/sitesApi';
import { PlusOutlined } from '@ant-design/icons';
import { Site } from '../sites/types';
import { Name } from './DocumentFamilyNameField';

const { Option } = Select;

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

const useModal = (): [boolean, () => void, () => void] => {
  const [isVisible, setIsVisible] = useState(false);

  const showModal = () => {
    setIsVisible(true);
  };

  const closeModal = () => {
    setIsVisible(false);
  };

  return [isVisible, showModal, closeModal];
};

const initialValues = {
  document_type_threshold: 75,
  therapy_tag_status_threshold: 75,
  lineage_threshold: 75,
};

interface AddDocumentFamilyPropTypes {
  closeModal: () => void;
  visible: boolean;
  doc: DocDocument;
}
export const AddDocumentFamily = ({ doc, closeModal, visible }: AddDocumentFamilyPropTypes) => {
  const { data: site } = useGetSiteQuery(doc.site_id);
  const [form] = Form.useForm();

  const onFinish = (values: FormData) => {
    form.resetFields();
    closeModal();
    console.log(values);
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
        <div className="ant-modal-footer mt-3">
          <Button onClick={onCancel}>Cancel</Button>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

export const DocumentFamily = ({ doc }: { doc: DocDocument }) => {
  const children = [];

  for (let i = 10; i < 36; i++) {
    children.push({ key: i.toString(36) + i, label: i.toString(36) + i });
  }
  const [options, setOptions] = useState([]);

  const [isModalVisible, showModal, closeModal] = useModal();

  return (
    <div className="flex space-x-8">
      <AddDocumentFamily closeModal={closeModal} visible={isModalVisible} doc={doc} />
      <Form.Item name="document_family" label="Document Family" className="flex-1">
        <Select mode="multiple" allowClear placeholder="None selected" defaultValue={[]}>
          {options.map(({ key, label }) => (
            <Option key={key}>{label}</Option>
          ))}
        </Select>
      </Form.Item>
      <Button className="flex-1 my-7" type="dashed" onClick={showModal}>
        <PlusOutlined />
        Add New Document Family
      </Button>
    </div>
  );
};

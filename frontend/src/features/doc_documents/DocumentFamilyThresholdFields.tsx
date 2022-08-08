import { Form, InputNumber } from 'antd';

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

export const initialThresholdValues = {
  document_type_threshold: 75,
  therapy_tag_status_threshold: 75,
  lineage_threshold: 75,
};

export function ThresholdFields() {
  return (
    <div className="flex space-x-8">
      <DocumentTypeThreshold />
      <TherapyTagStatusThreshold />
      <LineageThreshold />
    </div>
  );
}

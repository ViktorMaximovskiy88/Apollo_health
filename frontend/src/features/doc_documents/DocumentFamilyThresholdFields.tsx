import { Form, FormInstance, InputNumber } from 'antd';
import { Rule } from 'antd/lib/form';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';

const useMustMatchThreshold = ({
  docDocumentForm,
  thresholdType,
  thresholdName,
}: {
  docDocumentForm: FormInstance;
  thresholdType: string;
  thresholdName: 'document_type_threshold' | 'therapy_tag_status_threshold' | 'lineage_threshold';
}) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const documentType = Form.useWatch('document_type', docDocumentForm);

  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    siteId: doc?.site_id ?? '',
    documentType,
  });

  const mustMatchThreshold = () => ({
    async validator(_: Rule, threshold: number) {
      if (!documentFamilies) return;
      const selections = docDocumentForm.getFieldValue('document_families');
      const selectedDocumentFamilies = documentFamilies.filter((df) => selections.includes(df._id));
      for (const df of selectedDocumentFamilies) {
        if (threshold !== df[thresholdName]) {
          return Promise.reject(
            `Existing selected ${thresholdType} Confidence Threshold is different.
            Document Family "${df.name}" has a threshold of ${df[thresholdName]}%,
            and this Document Family has a threshold of ${threshold}%.`
          );
        }
      }
      return Promise.resolve();
    },
  });

  return mustMatchThreshold;
};

const DocumentTypeThreshold = ({ docDocumentForm }: { docDocumentForm: FormInstance }) => {
  const mustMatchThreshold = useMustMatchThreshold({
    docDocumentForm,
    thresholdType: 'Document Type',
    thresholdName: 'document_type_threshold',
  });
  return (
    <Form.Item
      name="document_type_threshold"
      label="Document Type Confidence Threshold"
      className="flex-1"
      rules={[
        mustMatchThreshold,
        { required: true, message: 'Please input a Document Type Confidence Threshold!' },
      ]}
      required
    >
      <InputNumber min={1} max={100} addonAfter="%" />
    </Form.Item>
  );
};
const TherapyTagStatusThreshold = ({ docDocumentForm }: { docDocumentForm: FormInstance }) => {
  const mustMatchThreshold = useMustMatchThreshold({
    docDocumentForm,
    thresholdType: 'Therapy Tag',
    thresholdName: 'therapy_tag_status_threshold',
  });
  return (
    <Form.Item
      name="therapy_tag_status_threshold"
      label="Therapy Tag Confidence Threshold"
      className="flex-1"
      rules={[
        mustMatchThreshold,
        { required: true, message: 'Please input a Therapy Tag Confidence Threshold!' },
      ]}
      required
    >
      <InputNumber min={1} max={100} addonAfter="%" />
    </Form.Item>
  );
};
const LineageThreshold = ({ docDocumentForm }: { docDocumentForm: FormInstance }) => {
  const mustMatchThreshold = useMustMatchThreshold({
    docDocumentForm,
    thresholdType: 'Lineage',
    thresholdName: 'lineage_threshold',
  });
  return (
    <Form.Item
      name="lineage_threshold"
      label="Lineage Confidence Threshold"
      className="flex-1"
      rules={[
        mustMatchThreshold,
        { required: true, message: 'Please input a Lineage Confidence Threshold!' },
      ]}
      required
    >
      <InputNumber min={1} max={100} addonAfter="%" />
    </Form.Item>
  );
};

export const initialThresholdValues = {
  document_type_threshold: 75,
  therapy_tag_status_threshold: 75,
  lineage_threshold: 75,
};

export function ThresholdFields({ docDocumentForm }: { docDocumentForm: FormInstance }) {
  return (
    <div className="flex space-x-8">
      <DocumentTypeThreshold docDocumentForm={docDocumentForm} />
      <TherapyTagStatusThreshold docDocumentForm={docDocumentForm} />
      <LineageThreshold docDocumentForm={docDocumentForm} />
    </div>
  );
}

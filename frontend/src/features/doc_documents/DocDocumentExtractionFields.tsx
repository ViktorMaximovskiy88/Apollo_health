import { useState } from 'react';
import { Form, Select, Switch } from 'antd';
import { DocDocument } from './types';

const languageCodes = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'other', label: 'Other' },
];

const Language = () => (
  <Form.Item name="lang_code" label="Language" className="flex-1">
    <Select options={languageCodes} />
  </Form.Item>
);

interface AutomatedContextExtractionPropTypes {
  setAutomatedExtraction: (automatedExtraction: boolean) => void;
}
const AutomatedContentExtraction = (props: AutomatedContextExtractionPropTypes) => (
  <Form.Item
    className="flex-1"
    name="automated_content_extraction"
    label="Automated Content Extraction"
    valuePropName="checked"
  >
    <Switch
      onChange={(checked: boolean) => {
        props.setAutomatedExtraction(checked);
      }}
    />
  </Form.Item>
);

const extractionOptions = [
  { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
  { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
  { value: 'MedigoldFormularyExtraction', label: 'Medigold Formulary Extraction' },
];

const ExtractionStrategy = () => (
  <Form.Item name="automated_content_extraction_class" label="Extraction Strategy">
    <Select options={extractionOptions} />
  </Form.Item>
);

export const ExtractionFields = ({ doc }: { doc: DocDocument }) => {
  const [automatedExtraction, setAutomatedExtraction] = useState(doc.automated_content_extraction);
  return (
    <>
      <div className="flex space-x-8">
        <Language />
        <AutomatedContentExtraction setAutomatedExtraction={setAutomatedExtraction} />
      </div>

      {automatedExtraction && <ExtractionStrategy />}
    </>
  );
};

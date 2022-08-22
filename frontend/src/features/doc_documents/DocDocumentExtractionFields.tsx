import { useState } from 'react';
import { Form, Select, Switch } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { LanguageCodes } from '../retrieved_documents/types';

const useAutomatedExtractionState = (): [boolean, (automatedExtraction: boolean) => void] => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  return useState<boolean>(doc?.automated_content_extraction ?? false);
};

const Language = () => (
  <Form.Item name="lang_code" label="Language" className="flex-1">
    <Select options={LanguageCodes} />
  </Form.Item>
);

const AutomatedContentExtraction = (props: {
  setAutomatedExtraction: (automatedExtraction: boolean) => void;
}) => (
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

export const ExtractionFields = () => {
  const [automatedExtraction, setAutomatedExtraction] = useAutomatedExtractionState();
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

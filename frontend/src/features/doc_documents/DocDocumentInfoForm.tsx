import { Checkbox, Form, Input } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';

import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { Translation } from './TranslationSelector';
import { DocDocumentInfoFormFamilyField } from './DocDocumentInfoFormFamilyField';
import { DocDocument } from './types';

interface DocDocumentInfoTypes {
  docDocument: DocDocument;
  onFieldChange: () => void;
}
export function DocDocumentInfoForm({ onFieldChange, docDocument }: DocDocumentInfoTypes) {
  // bandaid fix; painted into a corner
  const { docDocumentId, itemId } = useParams();
  const docId = docDocumentId ?? itemId;
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <>
      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>
      <div className="flex">
        <div className="mt-1">Internal Document&nbsp;</div>
        <Form.Item valuePropName="checked" name="internal_document">
          <Checkbox />
        </Form.Item>
      </div>
      <Hr />
      <DocumentClassification />
      <Translation />
      <Hr />
      <DocDocumentInfoFormFamilyField docDocument={docDocument} onFieldChange={onFieldChange} />
      <Hr />
      <DateFields onFieldChange={onFieldChange} />
      <Hr />
      <ExtractionFields />
    </>
  );
}

import { Checkbox, Radio } from 'antd';
import { useState } from 'react';
import { setDocumentTableLimit } from '../collections/documentsSlice';
import { ExtractionResultsDataTable } from '../extractions/ExtractionResultsDataTable';
import { DocDocument } from './types';

export function DocDocumentExtractionTab(props: { doc: DocDocument }) {
  const [delta, setDelta] = useState(false);
  return (
    <div className="flex flex-col h-full">
      <div>
        <Radio.Group
          className="flex pb-2"
          optionType="button"
          buttonStyle="solid"
          defaultValue={false}
          onChange={(e) => setDelta(e.target.value)}
        >
          <Radio.Button className="w-full text-center" value={false}>
            Full
          </Radio.Button>
          <Radio.Button className="w-full text-center" value={true}>
            Delta
          </Radio.Button>
        </Radio.Group>
      </div>
      <ExtractionResultsDataTable
        extractionId={props.doc.content_extraction_task_id}
        delta={delta}
      />
    </div>
  );
}

import { Button, Checkbox, Radio } from 'antd';
import { CheckboxValueType } from 'antd/lib/checkbox/Group';
import { useCallback, useState } from 'react';
import { ExtractionResultsDataTable } from '../extractions/ExtractionResultsDataTable';
import {
  useGetExtractionTaskQuery,
  useRunExtractionDeltaMutation,
} from '../extractions/extractionsApi';
import { DocDocument } from './types';

export function DocDocumentExtractionTab(props: { doc: DocDocument }) {
  const [delta, setDelta] = useState(false);
  const [deltaSubset, setDeltaSubset] = useState(['add', 'remove', 'edit']);
  const [createDeltaMutation] = useRunExtractionDeltaMutation();
  const createDelta = useCallback(async () => {
    await createDeltaMutation({ id: props.doc.content_extraction_task_id, docId: props.doc._id });
  }, [props.doc, createDeltaMutation]);

  const onChange = useCallback(
    (e: CheckboxValueType[]) => {
      setDeltaSubset(e.map((v) => v.toString()));
    },
    [setDeltaSubset]
  );

  const { data: extraction } = useGetExtractionTaskQuery(props.doc.content_extraction_task_id);
  const options = extraction
    ? [
        { label: `Add (${extraction.delta?.added})`, value: 'add' },
        { label: `Remove (${extraction.delta?.removed})`, value: 'remove' },
        { label: `Update (${extraction.delta?.updated})`, value: 'edit' },
      ]
    : [];

  const fullOptions = extraction
    ? [
        {
          label: `Translated (${
            Number(extraction.extraction_count) - Number(extraction.untranslated_count)
          })`,
          value: 'translated',
        },
        { label: `Untranslated (${extraction.untranslated_count})`, value: 'untranslated' },
      ]
    : [];
  const [fullSubset, setFullSubset] = useState(['translated', 'untranslated']);
  const onFullChange = useCallback(
    (e: CheckboxValueType[]) => {
      setFullSubset(e.map((v) => v.toString()));
    },
    [setFullSubset]
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex pb-2">
        <Radio.Group
          className="flex"
          optionType="button"
          buttonStyle="solid"
          defaultValue={false}
          onChange={(e) => setDelta(e.target.value)}
        >
          <Radio.Button value={false}>Full</Radio.Button>
          <Radio.Button value={true}>Delta</Radio.Button>
        </Radio.Group>
        {delta ? (
          <Checkbox.Group
            className="ml-4 align-middle"
            value={deltaSubset}
            onChange={onChange}
            options={options}
          />
        ) : (
          <Checkbox.Group
            className="ml-4 align-middle"
            value={fullSubset}
            onChange={onFullChange}
            options={fullOptions}
          />
        )}
        <div className="ml-auto">
          <Button onClick={createDelta}>Create Delta</Button>
        </div>
      </div>
      <ExtractionResultsDataTable
        extractionId={props.doc.content_extraction_task_id}
        delta={delta}
        deltaSubset={deltaSubset}
        fullSubset={fullSubset}
      />
    </div>
  );
}

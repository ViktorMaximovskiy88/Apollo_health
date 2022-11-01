import { DeleteFilled, MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Checkbox, Collapse, Form, Input, Select, Tabs } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { Tab } from 'rc-tabs/lib/interface';
import { ReactNode, useCallback, useState } from 'react';
import {
  useGetDocDocumentQuery,
  useLazyGetDocDocumentsQuery,
} from '../doc_documents/docDocumentApi';
import { useGetSiteQuery, useLazyGetSitesQuery } from '../sites/sitesApi';
import { RemoteSelect } from '../../components/RemoteSelect';
import { TranslationConfig } from './types';
import { CommentWall } from '../comments/CommentWall';

function TranslationFormContainer(props: { children: ReactNode }) {
  return <div className="max-w-xl">{props.children}</div>;
}

export function TableDetectionForm() {
  return (
    <TranslationFormContainer>
      <div className="flex space-x-4">
        <Form.Item className="grow" name={['detection', 'start_text']} label="Start Text">
          <Input />
        </Form.Item>
        <Form.Item name={['detection', 'start_page']} label="Start Page">
          <Input type="number" />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item className="grow" name={['detection', 'end_text']} label="End Text">
          <Input />
        </Form.Item>
        <Form.Item name={['detection', 'end_page']} label="End Page">
          <Input type="number" />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item
          className="grow"
          name={['detection', 'required_header_text']}
          label="Required Header Text"
        >
          <Input />
        </Form.Item>
        <Form.Item
          className="grow"
          name={['detection', 'exclude_header_text']}
          label="Exclude Header Text"
        >
          <Input />
        </Form.Item>
      </div>
    </TranslationFormContainer>
  );
}

export function TableBasicInfoForm() {
  const formSiteId = Form.useWatch(['sample', 'site_id']);
  const formDocId = Form.useWatch(['sample', 'doc_id']);

  const { data: site } = useGetSiteQuery(formSiteId, { skip: !formSiteId });
  const { data: doc } = useGetDocDocumentQuery(formDocId, { skip: !formDocId });
  const [getSites] = useLazyGetSitesQuery();
  const [getDocs] = useLazyGetDocDocumentsQuery();

  const siteOptions = useCallback(
    async (search: string) => {
      const { data } = await getSites({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((site) => ({ label: site.name, value: site._id }));
    },
    [getSites]
  );

  const documentOptions = useCallback(
    async (search: string) => {
      const { data } = await getDocs({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [
          { name: 'locations.site_id', operator: 'eq', type: 'string', value: formSiteId },
          { name: 'name', operator: 'contains', type: 'string', value: search },
        ],
      });
      if (!data) return [];
      return data.data.map((site) => ({ key: site._id, label: site.name, value: site._id }));
    },
    [formSiteId, getDocs]
  );

  const initialSiteOptions = site ? [{ value: site._id, label: site.name }] : [];
  const initialDocOptions = doc ? [{ value: doc._id, label: doc.name }] : [];

  return (
    <TranslationFormContainer>
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>
      <Form.Item name={['sample', 'site_id']} label="Site For Testing">
        <RemoteSelect
          className="w-full"
          placeholder="Select Site..."
          initialOptions={initialSiteOptions}
          fetchOptions={siteOptions}
        />
      </Form.Item>
      {formSiteId && (
        <Form.Item name={['sample', 'doc_id']} label="Document For Testing">
          <RemoteSelect
            className="w-full"
            placeholder="Select Document..."
            initialOptions={initialDocOptions}
            fetchOptions={documentOptions}
          />
        </Form.Item>
      )}
    </TranslationFormContainer>
  );
}
export function TableExtractionForm() {
  return (
    <TranslationFormContainer>
      <div className="flex space-x-4">
        <Form.Item
          className="grow"
          name={['extraction', 'required_columns']}
          label="Required Columns"
        >
          <Select mode="tags" />
        </Form.Item>
        <Form.Item className="grow" name={['extraction', 'banned_columns']} label="Banned Columns">
          <Select mode="tags" />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item
          className="grow"
          name={['extraction', 'merge_on_missing_columns']}
          label="Collapse on Missing Columns"
        >
          <Select mode="tags" />
        </Form.Item>
        <Form.Item name={['extraction', 'merge_strategy']} label="Merge Strategy">
          <Select
            options={[
              { label: 'Merge Above', value: 'UP' },
              { label: 'Merge Below', value: 'DOWN' },
            ]}
          />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item className="grow" name={['extraction', 'skip_rows']} label="Skip N Rows">
          <Input type="number" />
        </Form.Item>
        <Form.Item
          name={['extraction', 'skip_rows_first_table_only']}
          valuePropName="checked"
          label="First Page Only"
        >
          <Checkbox />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item
          className="grow"
          name={['extraction', 'start_table_text']}
          label="Start Table Text"
        >
          <Input />
        </Form.Item>
        <Form.Item className="grow" name={['extraction', 'end_table_text']} label="End Table Text">
          <Input />
        </Form.Item>
        <Form.Item className="grow" name={['extraction', 'max_font_size']} label="Max Font Size">
          <Input type="number" />
        </Form.Item>
      </div>
      <Form.Item name={['extraction', 'table_shape']} label="Table Defined By">
        <Select
          options={[
            { label: 'Lines', value: 'lines' },
            { label: 'Aligned Text', value: 'text' },
          ]}
        />
      </Form.Item>
      <Form.Item name={['extraction', 'explicit_headers']} label="Explicit Headers">
        <Select mode="tags" />
      </Form.Item>
      <div className="flex space-x-4">
        <Form.Item
          name={['extraction', 'explicit_column_lines']}
          className="grow"
          label="Explicit Column Lines"
        >
          <Select mode="tags" />
        </Form.Item>
        <Form.Item
          valuePropName="checked"
          name={['extraction', 'explicit_column_lines_only']}
          label="Explicit Only"
        >
          <Checkbox />
        </Form.Item>
      </div>
      <div className="flex space-x-4">
        <Form.Item className="grow" name={['extraction', 'snap_tolerance']} label="Snap Tolerance">
          <Input type="number" />
        </Form.Item>
        <Form.Item
          className="grow"
          name={['extraction', 'intersection_tolerance']}
          label="Intersection Tolerance"
        >
          <Input type="number" />
        </Form.Item>
      </div>
    </TranslationFormContainer>
  );
}

function AddColumnRule(props: { onClick: () => void }) {
  return (
    <Form.Item className="mt-4">
      <Button onClick={props.onClick} icon={<PlusOutlined />}>
        Column
      </Button>
    </Form.Item>
  );
}

function RemoveTranslationRule(props: { onClick: () => void }) {
  return <MinusCircleOutlined className="text-gray-500" onClick={props.onClick} />;
}
function AddTranslationRule(props: { onClick: () => void }) {
  return (
    <Form.Item className="mb-0">
      <Button onClick={props.onClick} icon={<PlusOutlined />}>
        Rule
      </Button>
    </Form.Item>
  );
}
function AddTierMapping(props: { onClick: () => void }) {
  return (
    <Form.Item>
      <Button onClick={props.onClick} icon={<PlusOutlined />}>
        Tier
      </Button>
    </Form.Item>
  );
}

function newColumnRule() {
  return {
    column: 'Column',
    rules: [],
  };
}
function newTranslationRule() {
  return {
    field: '',
    pattern: '',
    mappings: [],
  };
}

function PatternTranslationInput({ name, field }: { name: number; field: any }) {
  return (
    <>
      <Form.Item label="Pattern" name={[name, 'pattern']} {...field}>
        <Input />
      </Form.Item>
      <Form.Item
        label="Capture All"
        valuePropName="checked"
        name={[name, 'capture_all']}
        {...field}
      >
        <Checkbox />
      </Form.Item>
    </>
  );
}

function TierTranslationRow(props: {
  name: number;
  index: number;
  remove: (name: number) => void;
  field: any;
}) {
  const first = props.index === 0;
  return (
    <Input.Group className="space-x-2 flex">
      <Form.Item
        className="grow mb-2"
        label={first ? 'Text' : null}
        name={[props.name, 'pattern']}
        {...props.field}
      >
        <Input />
      </Form.Item>
      <Form.Item
        className="grow mb-2"
        label={first ? 'Action' : null}
        name={[props.name, 'translation']}
        {...props.field}
      >
        <Input />
      </Form.Item>
      <Form.Item className="mb-2" label={first ? ' ' : null}>
        <RemoveTranslationRule onClick={() => props.remove(props.name)} />
      </Form.Item>
    </Input.Group>
  );
}

function BvGRuleRow(props: {
  name: number;
  index: number;
  remove: (name: number) => void;
  field: any;
}) {
  const first = props.index === 0;
  const actions = [
    { label: 'Use Brand', value: 'brand' },
    { label: 'Use Generic', value: 'generic' },
    { label: 'Use Both', value: 'both' },
  ];
  return (
    <Input.Group className="space-x-2 flex">
      <Form.Item
        className="grow mb-2"
        label={first ? 'Text' : null}
        name={[props.name, 'pattern']}
        {...props.field}
      >
        <Input />
      </Form.Item>
      <Form.Item
        className="grow mb-2"
        label={first ? 'Tier' : null}
        name={[props.name, 'translation']}
        {...props.field}
      >
        <Select options={actions} />
      </Form.Item>
      <Form.Item className="mb-2" label={first ? ' ' : null}>
        <RemoveTranslationRule onClick={() => props.remove(props.name)} />
      </Form.Item>
    </Input.Group>
  );
}

function TierTranslationInput(props: { name: number; field: any }) {
  return (
    <Form.List name={[props.name, 'mappings']}>
      {(fields, { add, remove }, { errors }) => (
        <div className="px-12">
          {fields.map(({ key, name, ...field }, index) => (
            <TierTranslationRow key={key} name={name} field={field} remove={remove} index={index} />
          ))}
          <AddTierMapping onClick={() => add({ translation: '', pattern: '' })} />
        </div>
      )}
    </Form.List>
  );
}

function CodeTranslationInput(props: { name: number; field: any }) {
  return (
    <>
      <Form.Item name={[props.name, 'separator']} label="Strength Sep" className="w-24">
        <Input />
      </Form.Item>
      <Form.Item name={[props.name, 'separator2']} label="Form Sep" className="w-24">
        <Input />
      </Form.Item>
    </>
  );
}

function QLCTranslationInput(props: { name: number; field: any }) {
  const options = [
    { value: 'time', label: 'Time' },
    { value: 'quantity', label: 'Quantity' },
  ];
  return (
    <Form.Item className="w-32" name={[props.name, 'value']} label="Component">
      <Select options={options} />
    </Form.Item>
  );
}

function BvGTranslationInput(props: { name: number; field: any }) {
  return (
    <Form.List name={[props.name, 'mappings']}>
      {(fields, { add, remove }, { errors }) => (
        <div className="px-12">
          {fields.map(({ key, name, ...field }, index) => (
            <BvGRuleRow key={key} name={name} field={field} remove={remove} index={index} />
          ))}
          <Form.Item>
            <Button onClick={() => add({})} icon={<PlusOutlined />}>
              Action
            </Button>
          </Form.Item>
        </div>
      )}
    </Form.List>
  );
}

function TranslationRule(props: {
  column: number;
  name: number;
  remove: (name: number) => void;
  field: any;
}) {
  const options = [
    { value: 'PA', label: 'Prior Authorization' },
    { value: 'CPA', label: 'Conditional PA' },
    { value: 'QL', label: 'Quantity Limit' },
    { value: 'QLC', label: 'QL Component' },
    { value: 'SP', label: 'Specialty Pharmacy' },
    { value: 'ST', label: 'Step Therapy' },
    { value: 'Generic', label: 'Generic' },
    { value: 'Brand', label: 'Brand' },
    { value: 'BvG', label: 'Brand vs Generic' },
    { value: 'Tier', label: 'Tier' },
    { value: 'STPA', label: ' Step in Prior Authorization' },
    { value: 'MB', label: 'Medical Benefit' },
    { value: 'SCO', label: 'State Carve Out' },
    { value: 'DME', label: 'Durable Medical Equipment' },
  ];
  const field = Form.useWatch([
    'translation',
    'column_rules',
    props.column,
    'rules',
    props.name,
    'field',
  ]);
  return (
    <>
      <Input.Group className="space-x-2 flex">
        <Form.Item className="grow" label="Field" name={[props.name, 'field']} {...props.field}>
          <Select options={options} />
        </Form.Item>
        {['PA', 'CPA', 'QL', 'ST', 'SP', 'STPA', 'MB', 'SCO', 'DME'].includes(field) && (
          <PatternTranslationInput name={props.name} field={props.field} />
        )}
        {['Brand', 'Generic'].includes(field) && (
          <CodeTranslationInput name={props.name} field={props.field} />
        )}
        {field === 'QLC' && <QLCTranslationInput name={props.name} field={props.field} />}
        <Form.Item label=" ">
          <RemoveTranslationRule onClick={() => props.remove(props.name)} />
        </Form.Item>
      </Input.Group>
      {field === 'Tier' && <TierTranslationInput name={props.name} field={props.field} />}
      {field === 'BvG' && <BvGTranslationInput name={props.name} field={props.field} />}
    </>
  );
}

function ColumnRule(props: { name: number; field: any }) {
  return (
    <>
      <Form.Item label="Column" name={[props.name, 'column']} {...props.field}>
        <Input autoFocus />
      </Form.Item>
      <Form.Item label="Rules">
        <Form.List name={[props.name, 'rules']}>
          {(fields, { add, remove }, { errors }) => (
            <>
              {fields.map(({ key, name, ...field }) => (
                <TranslationRule
                  key={key}
                  column={props.name}
                  name={name}
                  field={field}
                  remove={remove}
                />
              ))}
              <AddTranslationRule onClick={() => add(newTranslationRule())} />
            </>
          )}
        </Form.List>
      </Form.Item>
    </>
  );
}

function ColumnPanelHeader(props: { name: number; remove: (name: number) => void }) {
  const header = Form.useWatch(['translation', 'column_rules', props.name, 'column']);
  return (
    <div className="flex">
      <span>{header ?? 'Column'}</span>
      <div className="ml-auto">
        <DeleteFilled className="text-gray-500" onClick={() => props.remove(props.name)} />
      </div>
    </div>
  );
}

export function TableTranslationForm(props: { initialValues?: Partial<TranslationConfig> }) {
  const [openPanels, setOpenPanels] = useState<string[]>(['0']);
  const [nextIndex, setNextIndex] = useState(
    props.initialValues?.translation?.column_rules.length ?? 0
  );

  const onChange = (nowOpenPanels: string | string[]) => {
    if (typeof nowOpenPanels === 'string') {
      setOpenPanels([nowOpenPanels]);
    } else {
      setOpenPanels(nowOpenPanels);
    }
  };

  return (
    <TranslationFormContainer>
      <Form.List name={['translation', 'column_rules']}>
        {(fields, { add, remove }, { errors }) => {
          function addColumn() {
            setOpenPanels(openPanels.concat([nextIndex.toString()]));
            setNextIndex(nextIndex + 1);
            add(newColumnRule(), nextIndex);
          }
          return (
            <>
              <Collapse activeKey={openPanels} onChange={onChange}>
                {fields.map(({ key, name, ...field }) => (
                  <Collapse.Panel
                    header={<ColumnPanelHeader name={name} remove={remove} />}
                    key={key}
                  >
                    <ColumnRule name={name} field={field} />
                  </Collapse.Panel>
                ))}
              </Collapse>
              <AddColumnRule onClick={addColumn} />
            </>
          );
        }}
      </Form.List>
    </TranslationFormContainer>
  );
}

export function TranslationForm(props: {
  form: FormInstance<any>;
  onFinish: (t: Partial<TranslationConfig>) => void;
  initialValues?: TranslationConfig;
}) {
  const tabs: Tab[] = [
    {
      key: 'basic',
      label: 'Basic',
      forceRender: true,
      children: <TableBasicInfoForm />,
    },
    {
      label: 'Detection',
      key: 'detection',
      forceRender: true,
      children: <TableDetectionForm />,
    },
    {
      label: 'Extraction',
      key: 'extraction',
      forceRender: true,
      children: <TableExtractionForm />,
    },
    {
      label: 'Translation',
      key: 'translation',
      forceRender: true,
      children: <TableTranslationForm initialValues={props.initialValues} />,
    },
  ];
  if (props.initialValues?._id) {
    tabs.push({
      key: 'comments',
      label: 'Notes',
      children: <CommentWall targetId={props.initialValues._id} />,
    });
  }
  return (
    <Form
      className="h-full"
      layout="vertical"
      form={props.form}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={props.initialValues}
    >
      <Tabs className="h-full ant-tabs-scroll" items={tabs} />
    </Form>
  );
}

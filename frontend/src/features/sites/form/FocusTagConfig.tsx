import { Button, Form, Input, Popover, Select, Switch } from 'antd';
import { MinusCircleOutlined, PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { FormListFieldData } from 'antd/lib/form/FormList';
import { useState } from 'react';
import { DocumentTypes } from '../../retrieved_documents/types';

import { Site } from '../types';

function Header() {
  const title = 'Seperators per document type to identify tag focus';
  const content = (
    <>
      <p className="whitespace-normal max-w-xs">
        For each document type, search for therapy and indication focus of the document will begin
        at the start separator text and end at the end separator text.
      </p>
    </>
  );
  return (
    <div className="flex items-center">
      <h4 className="mr-1 font-black">Tagging Focus Separators</h4>
      <Popover placement="right" title={title} content={content} className="mb-2 ml-px">
        <QuestionCircleOutlined />
      </Popover>
    </div>
  );
}

interface TypeInputPropTypes {
  name: number;
  field: { fieldKey?: number };
}
function DocTypeInput({ name, field }: TypeInputPropTypes) {
  return (
    <Form.Item
      {...field}
      label="Doc Type"
      name={[name, 'doc_type']}
      rules={[{ required: true, message: 'Required' }]}
      tooltip="Document Type to apply Separator to (Required)"
      className="mb-4 shrink-0 col-span-2"
    >
      <Select
        filterOption={(input, option) =>
          (option?.label as string).toLowerCase().includes(input.toLowerCase())
        }
        options={DocumentTypes}
        showSearch
      />
    </Form.Item>
  );
}

function SectionTypeInput({ name, field }: TypeInputPropTypes) {
  const options = [
    { value: 'THERAPY', label: 'Therapy' },
    { value: 'INDICATION', label: 'Indication' },
    { value: 'KEY', label: 'Key' },
  ];
  return (
    <Form.Item
      {...field}
      label="Section Type"
      name={[name, 'section_type']}
      rules={[{ required: true, message: 'Required' }]}
      tooltip="Section Type of Separator (Required)"
      className="mb-4 shrink-0 col-span-2"
    >
      <Select
        filterOption={(input, option) =>
          (option?.label as string).toLowerCase().includes(input.toLowerCase())
        }
        mode="multiple"
        options={options}
        showSearch
      />
    </Form.Item>
  );
}

interface InputPropTypes {
  disabled?: boolean;
  name: number;
  field: { fieldKey?: number };
}
function StartSeparatorInput({ disabled, name, field }: InputPropTypes) {
  return (
    <Form.Item
      {...field}
      label="Start Separator"
      name={[name, 'start_separator']}
      tooltip="Keyword to start focus search"
      className="mb-4 shrink-0 col-span-2"
    >
      <Input disabled={disabled} />
    </Form.Item>
  );
}

function EndSeparatorInput({ disabled, name, field }: InputPropTypes) {
  return (
    <Form.Item
      {...field}
      label="End Separator"
      name={[name, 'end_separator']}
      tooltip="Keyword to end focus search"
      className="mb-4 shrink-0 col-span-2"
    >
      <Input disabled={disabled} />
    </Form.Item>
  );
}

interface AllFocusPropTypes {
  onAllFocusToggle: Function;
  itemKey: number;
  name: number;
  field: { fieldKey?: number };
}
function AllFocusSwitch({ onAllFocusToggle, itemKey, name, field }: AllFocusPropTypes) {
  return (
    <div className="mb-0 shrink-0 col-span-2 font-black">
      <Form.Item
        {...field}
        className="mt-2"
        label="All Focus Tags"
        name={[name, 'all_focus']}
        tooltip="Make all tags the focus"
        valuePropName="checked"
      >
        <Switch onChange={(checked) => onAllFocusToggle(checked, itemKey)} />
      </Form.Item>
    </div>
  );
}

interface RemoveButtonPropTypes {
  fields: FormListFieldData[];
  remove: (index: number | number[]) => void;
  name: number;
}
function RemoveButton({ remove, name }: RemoveButtonPropTypes) {
  return (
    <div className="flex mb-0 mt-6 col-span-2 text-center">
      <Form.Item>
        <MinusCircleOutlined className="text-gray-500 mr-2" onClick={() => remove(name)} />
      </Form.Item>
      <label className="mt-1">Delete This Separator</label>
    </div>
  );
}
export function FocusTagConfig({ initialValues }: { initialValues: Partial<Site> }) {
  const initialState = () => {
    const configs = initialValues.scrape_method_configuration?.focus_section_configs;
    const focusStatus: { [key: string]: boolean | undefined } = {};
    if (configs) {
      configs.forEach((config, i) => {
        focusStatus[i] = config.all_focus;
      });
    }
    return focusStatus;
  };

  const [allFocus, setAllFocus] = useState<{ [key: string]: boolean | undefined }>(initialState());

  const handleAllFocusToggle = (checked: boolean, key: number) => {
    setAllFocus((prevState) => {
      const update = { ...prevState };
      update[key] = checked;
      return update;
    });
  };

  return (
    <Form.List name={['scrape_method_configuration', 'focus_section_configs']}>
      {(fields, { add, remove }, { errors }) => (
        <>
          <Header />
          {fields.map(({ key, name, ...field }) => (
            <Form.Item
              key={key}
              className="mb-2 pb-2 whitespace-nowrap border-solid border-x-0 border-t-0 border-slate-400"
              {...field}
            >
              <Input.Group className="grid grid-cols-4 space-x-1">
                <DocTypeInput name={name} field={field} />
                <SectionTypeInput name={name} field={field} />
                <StartSeparatorInput name={name} field={field} disabled={allFocus[key]} />
                <EndSeparatorInput name={name} field={field} disabled={allFocus[key]} />
                <AllFocusSwitch
                  onAllFocusToggle={handleAllFocusToggle}
                  itemKey={key}
                  name={name}
                  field={field}
                />
                <RemoveButton fields={fields} remove={remove} name={name} />
              </Input.Group>
            </Form.Item>
          ))}
          <Form.Item>
            <Button
              type="dashed"
              onClick={() =>
                add({
                  doc_type: '',
                  start_separator: '',
                  end_separator: '',
                })
              }
              icon={<PlusOutlined />}
            >
              Add Separator
            </Button>
            <Form.ErrorList errors={errors} />
          </Form.Item>
        </>
      )}
    </Form.List>
  );
}

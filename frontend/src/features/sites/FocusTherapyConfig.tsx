import { Button, Form, Input, Popover, Select, Switch, Tooltip } from 'antd';
import { MinusCircleOutlined, PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { FormListFieldData } from 'antd/lib/form/FormList';
import { useMemo, useState } from 'react';
import { DocumentTypes } from '../retrieved_documents/types';

import { Site } from './types';

interface HeaderPropTypes {
  fields: FormListFieldData[];
}
function FieldHeaders({ fields }: HeaderPropTypes) {
  if (fields.length === 0) {
    return null;
  }
  return (
    <div className="grid grid-cols-9 space-x-1 whitespace-nowrap">
      <div className="flex items-center col-span-2">
        <h4 className="mr-1">Document Type</h4>
        <Tooltip className="mb-2 ml-px" title="Document Type to apply Separator to (Required)">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 ">
        <h4 className="mr-1">Start Separator</h4>
        <Tooltip className="mb-2 ml-px" title="Keyword to start focus search (Required)">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">End Separator</h4>
        <Tooltip className="mb-2 ml-px" title="Keyword to end focus search">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">All Focus Therapies</h4>
        <Tooltip className="mb-2 ml-px" title="Make all tagged therapies the focus">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
    </div>
  );
}

function Header() {
  const title = 'Seperators per document type to identify therapy focus';
  const content = (
    <>
      <p className="whitespace-normal max-w-xs">
        For each document type, search for therapy focus of the document will begin at the start
        separator text and end at the end separator text.
      </p>
      <p>Limit one separator per document type</p>
    </>
  );
  return (
    <div className="flex items-center">
      <h4 className="mr-1">Therapy Focus Separators</h4>
      <Popover placement="right" title={title} content={content} className="mb-2 ml-px">
        <QuestionCircleOutlined />
      </Popover>
    </div>
  );
}

interface TypeInputPropTypes {
  name: number;
  field: { fieldKey?: number };
  itemKey: number;
  handleSelect: (value: string, key: number) => void;
  options: { label: string }[];
}
function TypeInput({ name, itemKey, field, handleSelect, options }: TypeInputPropTypes) {
  return (
    <Form.Item
      {...field}
      name={[name, 'doc_type']}
      rules={[{ required: true, message: 'Required' }]}
      className="mb-0 shrink-0 col-span-2"
    >
      <Select
        filterOption={(input, option) =>
          (option?.label as string).toLowerCase().includes(input.toLowerCase())
        }
        onChange={(value, option) => handleSelect(value, itemKey)}
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
  const rules = disabled ? undefined : [{ required: true, message: 'Required' }];
  return (
    <Form.Item
      {...field}
      name={[name, 'start_separator']}
      rules={rules}
      className="mb-0 shrink-0 col-span-2"
    >
      <Input disabled={disabled} />
    </Form.Item>
  );
}

function EndSeparatorInput({ disabled, name, field }: InputPropTypes) {
  return (
    <Form.Item {...field} name={[name, 'end_separator']} className="mb-0 shrink-0 col-span-2">
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
    <Form.Item
      {...field}
      name={[name, 'all_focus']}
      valuePropName="checked"
      className="mb-0 shrink-0 col-span-2 text-center"
    >
      <Switch onChange={(checked) => onAllFocusToggle(checked, itemKey)} />
    </Form.Item>
  );
}

interface RemoveButtonPropTypes {
  fields: FormListFieldData[];
  itemKey: number;
  remove: (index: number | number[]) => void;
  updateTypes: (value: string | null, key: number) => void;
  name: number;
}
function RemoveButton({ itemKey, remove, updateTypes, name }: RemoveButtonPropTypes) {
  const handleRemove = () => {
    updateTypes(null, itemKey);
    remove(name);
  };

  return (
    <Form.Item className="mb-0">
      <MinusCircleOutlined className="text-gray-500" onClick={handleRemove} />
    </Form.Item>
  );
}
export function FocusTherapyConfig({ initialValues }: { initialValues: Partial<Site> }) {
  const initialState = () => {
    const configs = initialValues.scrape_method_configuration?.focus_therapy_configs;
    const selectedOptions: { [key: string]: string } = {};
    const focusStatus: { [key: string]: boolean | undefined } = {};
    if (configs) {
      configs.forEach((config, i) => {
        selectedOptions[i] = config.doc_type;
        focusStatus[i] = config.all_focus;
      });
    }
    return { selectedOptions, focusStatus };
  };

  const [selectedOptions, setCurrentOptions] = useState<{ [key: string]: string | null }>(
    initialState().selectedOptions
  );
  const [allFocus, setAllFocus] = useState<{ [key: string]: boolean | undefined }>(
    initialState().focusStatus
  );
  const typeOptions = useMemo(() => {
    const currentOptions = Object.keys(selectedOptions).map((key) => selectedOptions[key]);
    const options = DocumentTypes.filter((option) => !currentOptions.includes(option.value));
    return options;
  }, [selectedOptions]);

  const handleTypeSelect = (value: string | null, key: number) => {
    setCurrentOptions((prevState) => {
      const update = { ...prevState };
      update[key] = value;
      return update;
    });
  };

  const handleAllFocusToggle = (checked: boolean, key: number) => {
    setAllFocus((prevState) => {
      const update = { ...prevState };
      update[key] = checked;
      return update;
    });
  };

  return (
    <Form.List name={['scrape_method_configuration', 'focus_therapy_configs']}>
      {(fields, { add, remove }, { errors }) => (
        <>
          <Header />
          <FieldHeaders fields={fields} />
          {fields.map(({ key, name, ...field }) => (
            <Form.Item key={key} className="mb-2 whitespace-nowrap" {...field}>
              <Input.Group className="grid grid-cols-9 space-x-1">
                <TypeInput
                  itemKey={key}
                  name={name}
                  field={field}
                  options={typeOptions}
                  handleSelect={handleTypeSelect}
                />
                <StartSeparatorInput name={name} field={field} disabled={allFocus[key]} />
                <EndSeparatorInput name={name} field={field} disabled={allFocus[key]} />
                <AllFocusSwitch
                  onAllFocusToggle={handleAllFocusToggle}
                  itemKey={key}
                  name={name}
                  field={field}
                />
                <RemoveButton
                  fields={fields}
                  itemKey={key}
                  remove={remove}
                  updateTypes={handleTypeSelect}
                  name={name}
                />
              </Input.Group>
            </Form.Item>
          ))}
          {typeOptions.length > 0 && (
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
          )}
        </>
      )}
    </Form.List>
  );
}

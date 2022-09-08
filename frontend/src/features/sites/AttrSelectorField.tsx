import {
  AutoComplete,
  Button,
  Select,
  Checkbox,
  Form,
  Input,
  Popover,
  Tooltip,
  Typography,
} from 'antd';
import { MinusCircleOutlined, PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { FormListFieldData } from 'antd/lib/form/FormList';
import { useEffect, useState } from 'react';

import { Hr } from '../../components';

interface InputPropTypes {
  displayLabel?: boolean;
  name: (string | number)[];
  field?: { fieldKey?: number };
}

interface HeaderPropTypes {
  fields: FormListFieldData[];
}
function FieldHeaders({ fields }: HeaderPropTypes) {
  if (fields.length === 0) {
    return null;
  }
  return (
    <div className="grid grid-cols-10 space-x-1 whitespace-nowrap">
      <div className="flex items-center col-span-2">
        <h4 className="mr-1">Element Name</h4>
        <Tooltip
          className="mb-2 ml-px cursor-help"
          title="Elements to search inside of for attribute. Example: <a> or <li>"
        >
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2">
        <h4 className="mr-1">Attr Name</h4>
        <Tooltip
          className="mb-2 ml-px cursor-help"
          title="Attributes whose name contain the search term"
        >
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 ">
        <h4 className="mr-1">Attr Value</h4>
        <Tooltip
          className="mb-2 ml-px cursor-help"
          title="Attributes whose value contain the search term"
        >
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">Contains Text</h4>
        <Tooltip className="mb-2 ml-px cursor-help" title="Tags that contain the search term'">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">Is Resource</h4>
        <Tooltip
          className="mb-2 ml-px cursor-help"
          title="Attribute with matching Attribute Name contains a direct
      link to the document"
        >
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
    </div>
  );
}

function Header() {
  const { Text } = Typography;
  const contentItems = [
    <div key="1">
      <p>
        <Text strong>Examples:</Text> The following configurations will match the elements below
      </p>
    </div>,
    <Hr key="2" />,
    <div key="3">
      <p>
        <Text strong>Element Name:</Text> a <br />
        <Text strong>Attr Name:</Text> onclick <br />
        <Text strong>Attr Value:</Text> /policy/ <br />
        <Text strong>Contains Text:</Text> Download
      </p>
      <Text code>&lt;a onclick="/documents/policy/file.pdf"&gt;Download File&lt;/a&gt;</Text>
    </div>,
    <Hr key="4" />,
    <div key="5">
      <p>
        <Text strong>Element Name:</Text> a <br />
        <Text strong>Attr Name:</Text> data- <br />
        <Text strong>Attr Value:</Text>
        <br />
        <Text strong>Contains Text:</Text>
      </p>
      <Text code>&lt;a data-v-abc123="getDocument"&gt;Download File&lt;/a&gt;</Text>
    </div>,
  ];

  const title = (
    <Text strong>Custom Selectors to Search Specific Attributes on &lt;a/&gt; Tags</Text>
  );
  return (
    <div className="flex items-center">
      <h4 className="mr-1">Custom Selectors</h4>
      <Popover
        placement="right"
        title={title}
        content={contentItems}
        className="mb-2 ml-px cursor-help"
      >
        <QuestionCircleOutlined />
      </Popover>
    </div>
  );
}

export function ElementInput({ displayLabel, name, field }: InputPropTypes) {
  const defaultOptions = [
    { label: 'a', value: 'a' },
    { label: 'p', value: 'p' },
    { label: 'li', value: 'li' },
    { label: 'div', value: 'div' },
    { label: 'span', value: 'span' },
    { label: 'input', value: 'input' },
  ];
  const [options, setOptions] = useState<{ value: string }[]>([]);

  const onSearch = (searchText: string) => {
    if (searchText) {
      const newOptions = defaultOptions.filter((option) => option.label.includes(searchText));
      const topOptions = newOptions.slice(0, 3);
      setOptions(topOptions);
    } else {
      setOptions([]);
    }
  };

  const label = displayLabel ? 'Element Name' : undefined;
  const tooltip = displayLabel
    ? 'Elements to search inside of for attribute. Example: <a> or <li>'
    : undefined;
  const nameProp = [...name, 'attr_element'];
  return (
    <Form.Item
      {...field}
      name={nameProp}
      className="mb-0 shrink-0 col-span-2"
      label={label}
      tooltip={tooltip}
    >
      <AutoComplete defaultActiveFirstOption={false} onSearch={onSearch} options={options} />
    </Form.Item>
  );
}

export function NameInput({ displayLabel, name, field }: InputPropTypes) {
  const defaultOptions = [
    { label: 'aria-label', value: 'aria-label' },
    { label: 'class', value: 'class' },
    { label: 'data-', value: 'data-' },
    { label: 'id', value: 'id' },
    { label: 'onclick', value: 'onclick' },
    { label: 'style', value: 'style' },
  ];
  const [options, setOptions] = useState<{ value: string }[]>([]);

  const onSearch = (searchText: string) => {
    if (searchText) {
      const newOptions = defaultOptions.filter((option) => option.label.includes(searchText));
      const topOptions = newOptions.slice(0, 3);
      setOptions(topOptions);
    } else {
      setOptions([]);
    }
  };

  const nameProp = [...name, 'attr_name'];
  const label = displayLabel ? 'Attr Name' : undefined;
  const tooltip = displayLabel ? 'Attributes whose name contain the search term' : undefined;
  return (
    <Form.Item
      {...field}
      name={nameProp}
      label={label}
      rules={[{ required: true, message: 'Required' }]}
      tooltip={tooltip}
      className="mb-0 shrink-0 col-span-2"
    >
      <AutoComplete defaultActiveFirstOption={false} onSearch={onSearch} options={options} />
    </Form.Item>
  );
}

export function ValueInput({ displayLabel, name, field }: InputPropTypes) {
  const nameProp = [...name, 'attr_value'];
  const label = displayLabel ? 'Attr Value' : undefined;
  const tooltip = displayLabel ? 'Attributes whose value contain the search term' : undefined;
  return (
    <Form.Item
      {...field}
      name={nameProp}
      label={label}
      tooltip={tooltip}
      className="mb-0 shrink-0 col-span-2"
    >
      <Input />
    </Form.Item>
  );
}

export function ContainsTextInput({ displayLabel, name, field }: InputPropTypes) {
  const nameProp = [...name, 'has_text'];
  const label = displayLabel ? 'Contains Text' : undefined;
  const tooltip = displayLabel ? 'Tags that contain the search term' : undefined;
  return (
    <Form.Item
      {...field}
      name={nameProp}
      label={label}
      tooltip={tooltip}
      className="mb-0 shrink-0 col-span-2"
    >
      <Input />
    </Form.Item>
  );
}

export function IsResourceAddress({ displayLabel, name, field }: InputPropTypes) {
  const nameProp = [...name, 'resource_address'];
  const label = displayLabel ? 'Is Resource' : undefined;
  const tooltip = displayLabel
    ? 'Attribute with matching Attribute Name contains a direct link to the document'
    : undefined;
  return (
    <Form.Item
      {...field}
      name={nameProp}
      label={label}
      tooltip={tooltip}
      valuePropName="checked"
      className="mb-0 shrink-0"
    >
      <Checkbox className="flex justify-center" />
    </Form.Item>
  );
}

interface RemoveButtonPropTypes {
  fields: FormListFieldData[];
  remove: (index: number | number[]) => void;
  name: number;
}
function RemoveButton({ remove, name }: RemoveButtonPropTypes) {
  return (
    <Form.Item className="mb-0">
      <MinusCircleOutlined className="text-gray-500" onClick={() => remove(name)} />
    </Form.Item>
  );
}

export function AttrSelectors() {
  return (
    <Form.List name={['scrape_method_configuration', 'attr_selectors']}>
      {(fields, { add, remove }, { errors }) => (
        <>
          <Header />
          <FieldHeaders fields={fields} />
          {fields.map(({ key, name, ...field }) => (
            <Form.Item key={key} className="mb-2 whitespace-nowrap" {...field}>
              <Input.Group className="grid grid-cols-10 space-x-1">
                <ElementInput name={[name]} field={field} />
                <NameInput name={[name]} field={field} />
                <ValueInput name={[name]} field={field} />
                <ContainsTextInput name={[name]} field={field} />
                <IsResourceAddress name={[name]} field={field} />
                <RemoveButton fields={fields} remove={remove} name={name} />
              </Input.Group>
            </Form.Item>
          ))}
          <Form.Item>
            <Button
              type="dashed"
              onClick={() =>
                add({
                  attr_name: '',
                  attr_value: '',
                  has_text: '',
                  resource_address: false,
                })
              }
              icon={<PlusOutlined />}
            >
              Add Custom Selector
            </Button>
            <Form.ErrorList errors={errors} />
          </Form.Item>
        </>
      )}
    </Form.List>
  );
}

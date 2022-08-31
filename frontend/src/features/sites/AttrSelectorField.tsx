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
import { useState } from 'react';

import { Hr } from '../../components';

interface InputPropTypes {
  name: number;
  field: { fieldKey?: number };
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
        <h4 className="mr-1">Attr Element</h4>
        <Tooltip
          className="mb-2 ml-px"
          title="Attribute element to search against. Example: <a> or <li>"
        >
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2">
        <h4 className="mr-1">Attr Name</h4>
        <Tooltip className="mb-2 ml-px" title="Text in name of attribute to search for">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 ">
        <h4 className="mr-1">Attr Value</h4>
        <Tooltip className="mb-2 ml-px" title="Attributes whose value contain the search term">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">Contains Text</h4>
        <Tooltip className="mb-2 ml-px" title="<a/> tags that contain the search term">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>
      <div className="flex items-center col-span-2 mr-1">
        <h4 className="mr-1">Is Resource</h4>
        <Tooltip
          className="mb-2 ml-px"
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
        <Text strong>Attr Element:</Text> element <br />
        <Text strong>Attr Name:</Text> onclick <br />
        <Text strong>Attr Value:</Text> /policy/ <br />
        <Text strong>Contains Text:</Text> Download
      </p>
      <Text code>&lt;a onclick="/documents/policy/file.pdf"&gt;Download File&lt;/a&gt;</Text>
    </div>,
    <Hr key="4" />,
    <div key="5">
      <p>
        <Text strong>Attr Element:</Text> element <br />
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
      <Popover placement="right" title={title} content={contentItems} className="mb-2 ml-px">
        <QuestionCircleOutlined />
      </Popover>
    </div>
  );
}

function ElementSelect({ name, field }: InputPropTypes) {
  const elements = [
    { value: 'a', label: 'a' },
    { value: 'li', label: 'li' },
    { value: 'span', label: 'span' },
    { value: 'p', label: 'p' },
  ];

  return (
    <Form.Item {...field} name={[name, 'attr_element']}>
      <Select defaultValue={{ label: 'a', value: 'a' }} options={elements} />
    </Form.Item>
  );
}

function NameInput({ name, field }: InputPropTypes) {
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
      let newOptions = defaultOptions.filter((option) => option.label.includes(searchText));
      newOptions = newOptions.slice(0, 3);
      setOptions(newOptions);
    } else {
      setOptions([]);
    }
  };

  return (
    <Form.Item
      {...field}
      name={[name, 'attr_name']}
      rules={[{ required: true, message: 'Required' }]}
      className="mb-0 shrink-0 col-span-2"
    >
      <AutoComplete defaultActiveFirstOption={false} onSearch={onSearch} options={options} />
    </Form.Item>
  );
}

function ValueInput({ name, field }: InputPropTypes) {
  return (
    <Form.Item {...field} name={[name, 'attr_value']} className="mb-0 shrink-0 col-span-2">
      <Input />
    </Form.Item>
  );
}

function ContainsTextInput({ name, field }: InputPropTypes) {
  return (
    <Form.Item
      {...field}
      name={[name, 'has_text']}
      className="mb-0 shrink-0 col-span-2"
      tooltip="Search for text contained within matching element"
    >
      <Input />
    </Form.Item>
  );
}

function IsResourceAddress({ name, field }: InputPropTypes) {
  return (
    <Form.Item
      {...field}
      name={[name, 'resource_address']}
      tooltip="Attribute contains path to document"
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
                <ElementSelect name={name} field={field} />
                <NameInput name={name} field={field} />
                <ValueInput name={name} field={field} />
                <ContainsTextInput name={name} field={field} />
                <IsResourceAddress name={name} field={field} />
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

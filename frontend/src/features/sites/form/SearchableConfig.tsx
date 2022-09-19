import { Input, Form, Select, Switch } from 'antd';
import { SearchableType } from '../types';
import { ElementInput, NameInput, ValueInput, ContainsTextInput } from './AttrSelectorField';

export function SearchableConfig() {
  const isSearchable = Form.useWatch(['scrape_method_configuration', 'searchable']);

  const searchableTypes = [
    { value: SearchableType.CPTCodes, label: 'CPT Codes' },
    { value: SearchableType.JCodes, label: 'JCodes' },
  ];
  const inputName = ['scrape_method_configuration', 'searchable_input'];
  const submitName = ['scrape_method_configuration', 'searchable_submit'];
  const groupClass = isSearchable ? 'border-solid border-slate-300 rounded p-2 pb-0' : undefined;
  return (
    <div className={groupClass}>
      <Form.Item
        name={['scrape_method_configuration', 'searchable']}
        label="Searchable"
        tooltip={'Site should be searched using CPT or JCodes'}
        valuePropName="checked"
      >
        <Switch className="flex justify-center" />
      </Form.Item>
      {isSearchable && (
        <>
          <Form.Item
            name={['scrape_method_configuration', 'searchable_type']}
            label="Searchable Type"
            rules={[{ required: true, message: 'Required' }]}
            tooltip={'Type of inputs to search for'}
          >
            <Select options={searchableTypes} />
          </Form.Item>
          <Form.Item
            name={inputName}
            label="Searchable Input"
            tooltip={'Input field for search terms'}
          >
            <Input.Group className="grid grid-cols-10 space-x-1">
              <ElementInput displayLabel name={inputName} />
              <NameInput displayLabel name={inputName} />
              <ValueInput displayLabel name={inputName} />
              <ContainsTextInput displayLabel name={inputName} />
            </Input.Group>
          </Form.Item>
          <Form.Item
            name={submitName}
            label="Searchable Submit Button"
            tooltip={'Button to trigger search'}
          >
            <Input.Group className="grid grid-cols-10 space-x-1">
              <ElementInput displayLabel name={submitName} />
              <NameInput displayLabel name={submitName} />
              <ValueInput displayLabel name={submitName} />
              <ContainsTextInput displayLabel name={submitName} />
            </Input.Group>
          </Form.Item>
        </>
      )}
    </div>
  );
}

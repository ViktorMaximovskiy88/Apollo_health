import { QuestionCircleOutlined } from '@ant-design/icons';
import { Input, Form, Switch, Select, Tooltip } from 'antd';
import { SearchableType } from '../types';
import { playbookValidator } from './utils';
import { ElementInput, NameInput, ValueInput, ContainsTextInput } from './AttrSelectorField';

export function SearchTokens() {
  const isSearchable: boolean = Form.useWatch(['scrape_method_configuration', 'searchable']);

  const searchableTypes = [
    { value: SearchableType.CPTCodes, label: 'CPT Codes' },
    { value: SearchableType.JCodes, label: 'JCodes' },
  ];

  const inputName = ['scrape_method_configuration', 'searchable_input'];
  const submitName = ['scrape_method_configuration', 'searchable_submit'];

  const groupDivClass = isSearchable ? 'border-solid border-slate-300 rounded p-2 pb-0' : undefined;
  const groupLabelClass = isSearchable ? 'text-lg' : undefined;

  const SearchablePlaybook = () => (
    <div>
      <div>
        Searchable Playbook
        <Tooltip className="ml-2" placement="right" title="Run playwright on each code iteration">
          <QuestionCircleOutlined />
        </Tooltip>
      </div>

      <Form.Item
        name={['scrape_method_configuration', 'searchable_playbook']}
        rules={[
          {
            required: false,
          },
          playbookValidator(),
        ]}
      >
        <Input.TextArea />
      </Form.Item>
    </div>
  );

  const [form] = Form.useForm();

  console.log(form.getFieldsValue(['scrape_method_configuration']));

  return (
    <div className={groupDivClass}>
      <Form.Item
        name={['scrape_method_configuration', 'searchable']}
        label={<span className={groupLabelClass}>Search Tokens</span>}
        tooltip={'Site should be searched using CPT or JCodes'}
        valuePropName="checked"
      >
        <Switch className="flex justify-center" />
      </Form.Item>
      {isSearchable ? (
        <>
          <Form.Item
            name={['scrape_method_configuration', 'searchable_type']}
            label="Searchable Type"
            rules={[{ required: true, message: 'Required' }]}
            tooltip={'Type of inputs to search for'}
          >
            <Select options={searchableTypes} mode="multiple" />
          </Form.Item>
          <Form.Item
            name={inputName}
            label="ID Search Input"
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
            label="ID Search Submit Button"
            tooltip={'Button to trigger search'}
          >
            <Input.Group className="grid grid-cols-10 space-x-1">
              <ElementInput displayLabel name={submitName} rules={undefined} />
              <NameInput displayLabel name={submitName} rules={undefined} />
              <ValueInput displayLabel name={submitName} />
              <ContainsTextInput displayLabel name={submitName} />
            </Input.Group>
            <br />
          </Form.Item>
        </>
      ) : null}

      <SearchablePlaybook />
    </div>
  );
}

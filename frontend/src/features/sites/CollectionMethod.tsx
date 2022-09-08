import { Checkbox, Input, Form, FormInstance, Select, Radio, Tooltip, Switch } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { CollectionMethod, Site } from './types';
import { useGetProxiesQuery } from '../proxies/proxiesApi';
import {
  AttrSelectors,
  ElementInput,
  NameInput,
  ValueInput,
  ContainsTextInput,
} from './AttrSelectorField';
import { FocusTherapyConfig } from './FocusTherapyConfig';

function CollectionMethodRadio() {
  const collections = [
    { value: CollectionMethod.Automated, label: 'Automated' },
    { value: CollectionMethod.Manual, label: 'Manual' },
  ];

  return (
    <Form.Item name="collection_method" label="Collection Method">
      <Radio.Group>
        {collections.map((col) => {
          return (
            <Radio key={col.value} value={col.value}>
              {col.label}
            </Radio>
          );
        })}
      </Radio.Group>
    </Form.Item>
  );
}

function ScrapeMethod() {
  const scrapes = [
    { value: 'SimpleDocumentScrape', label: 'Simple Document Scrape' },
    { value: 'BrowserDocumentScrape', label: 'Browser Document Scrape' },
    { value: 'MyPrimeSearchableScrape', label: 'MyPrime Searchable Scrape' },
  ];

  return (
    <Form.Item name="scrape_method" label="Scrape Method">
      <Select options={scrapes} />
    </Form.Item>
  );
}

function DocumentExtensions() {
  const extensions = [
    { value: 'pdf', label: 'PDF (.pdf)' },
    { value: 'xlsx', label: 'Excel (.xlsx)' },
    { value: 'docx', label: 'Word (.docx)' },
    { value: 'html', label: 'HTML (.html)' },
  ];

  return (
    <Form.Item
      name={['scrape_method_configuration', 'document_extensions']}
      label="Document Extensions"
    >
      <Select mode="multiple" options={extensions} />
    </Form.Item>
  );
}

function UrlKeywords() {
  return (
    <Form.Item name={['scrape_method_configuration', 'url_keywords']} label="URL Keywords">
      <Select mode="tags" />
    </Form.Item>
  );
}

function ProxyExclusions() {
  const { data: proxies } = useGetProxiesQuery();

  const proxyOptions = proxies?.map((proxy) => ({
    label: proxy.name,
    value: proxy._id,
  }));

  return (
    <Form.Item name={['scrape_method_configuration', 'proxy_exclusions']} label="Proxy Exclusions">
      <Select mode="multiple" options={proxyOptions} />
    </Form.Item>
  );
}

function WaitFor() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'wait_for']}
      label={
        <>
          <span style={{ marginRight: '5px' }}>Wait For</span>
          <Tooltip
            placement="right"
            title="Collection will wait for specific words to appear before continuing."
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Select mode="tags" />
    </Form.Item>
  );
}

function WaitForTimeout() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'wait_for_timeout_ms']}
      label={
        <>
          <span style={{ marginRight: '5px' }}>Wait For Timeout (ms)</span>
          <Tooltip
            placement="right"
            title="Collection will wait for specifed milliseconds before executing the page scrape."
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Input
        type={'number'}
        onFocus={(e: any) => e.target.select()}
        step={100}
        min={0}
        max={5000}
      />
    </Form.Item>
  );
}

function SearchInFrames() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'search_in_frames']}
      valuePropName="checked"
      label={
        <>
          <span style={{ marginRight: '5px' }}>Search in frames</span>
          <Tooltip placement="right" title="Run the page scrape within an iframe">
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Switch />
    </Form.Item>
  );
}

function AllowDocDocUpdate() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'allow_docdoc_updates']}
      valuePropName="checked"
      label={
        <>
          <span style={{ marginRight: '5px' }}>Allow Doc Document Updates</span>
          <Tooltip
            placement="right"
            title="Overwrite existing Therapy and Indication Tags on Doc Document during collection"
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Switch />
    </Form.Item>
  );
}

function SearchableConfig({ isSearchable }: { isSearchable: boolean }) {
  const searchableTypes = [
    { value: 'CPT Codes', label: 'CPT Codes' },
    { value: 'JCodes', label: 'JCodes' },
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
          <Form.Item name={inputName} label="Searchable Input">
            <Input.Group className="grid grid-cols-10 space-x-1">
              <ElementInput displayLabel name={inputName} />
              <NameInput displayLabel name={inputName} />
              <ValueInput displayLabel name={inputName} />
              <ContainsTextInput displayLabel name={inputName} />
            </Input.Group>
          </Form.Item>
          <Form.Item name={submitName} label="Searchable Submit">
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

function ScrapeMethodConfiguration({
  initialValues,
  isSearchable,
}: {
  initialValues: Partial<Site>;
  isSearchable: boolean;
}) {
  return (
    <Form.Item name="scrape_method_configuration">
      <DocumentExtensions />
      <UrlKeywords />
      <AttrSelectors />
      <SearchableConfig isSearchable={isSearchable} />
      <ProxyExclusions />
      <WaitFor />
      <WaitForTimeout />
      <SearchInFrames />
      <FocusTherapyConfig initialValues={initialValues} />
      <AllowDocDocUpdate />
    </Form.Item>
  );
}

function Schedule() {
  const schedules = [
    { value: '0 16 * * *', label: 'Daily' },
    { value: '0 16 * * 0', label: 'Weekly' },
    { value: '0 16 1 * *', label: 'Monthly' },
  ];

  return (
    <Form.Item name="cron" label="Schedule">
      <Select options={schedules} />
    </Form.Item>
  );
}

function FollowLinks(props: { followLinks: boolean; form: FormInstance }) {
  function validateFollowLinks(fieldInfo: any, value: string) {
    if (value.length === 0) {
      const namePaths = [
        ['scrape_method_configuration', 'follow_link_keywords'],
        ['scrape_method_configuration', 'follow_link_url_keywords'],
      ];
      const currentNamePath = fieldInfo.field.split('.');
      const otherNamePath = namePaths
        .filter((path) => {
          return !path.every((ele) => currentNamePath.includes(ele));
        })
        .flat();
      const otherValue = props.form.getFieldValue(otherNamePath);

      if (otherValue.length === 0) {
        return Promise.reject(
          new Error('You must provide a Link or URL Keyword with Follow Links enabled')
        );
      }
    }

    return Promise.resolve();
  }

  return (
    <div className="flex space-x-5">
      <Form.Item
        name={['scrape_method_configuration', 'follow_links']}
        label="Follow Links"
        valuePropName="checked"
      >
        <Checkbox className="flex justify-center" />
      </Form.Item>
      {props.followLinks && (
        <div className="flex grow space-x-5">
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'follow_link_keywords']}
            label="Follow Link Keywords"
            rules={[
              {
                validator: (field, value) => validateFollowLinks(field, value),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'follow_link_url_keywords']}
            label="Follow Link URL Keywords"
            rules={[
              {
                validator: (field, value) => validateFollowLinks(field, value),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
        </div>
      )}
    </div>
  );
}

interface CollectionMethodPropTypes {
  followLinks: boolean;
  form: FormInstance;
  initialValues: Partial<Site>;
  isSearchable: boolean;
}
export function CollectionMethodComponent({
  followLinks,
  form,
  initialValues,
  isSearchable,
}: CollectionMethodPropTypes) {
  return (
    <>
      <CollectionMethodRadio />
      <Form.Item
        noStyle
        shouldUpdate={(prevValues, currentValues) =>
          prevValues.collection_method !== currentValues.collection_method
        }
      >
        {({ getFieldValue }) =>
          getFieldValue('collection_method') === CollectionMethod.Automated ? (
            <>
              <ScrapeMethod />
              <ScrapeMethodConfiguration
                initialValues={initialValues}
                isSearchable={isSearchable}
              />
              <Schedule />
              <FollowLinks followLinks={followLinks} form={form} />
            </>
          ) : null
        }
      </Form.Item>
    </>
  );
}

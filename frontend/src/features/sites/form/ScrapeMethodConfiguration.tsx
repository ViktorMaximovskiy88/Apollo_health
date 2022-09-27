import { Input, Form, Select, Tooltip, Switch } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

import { useGetProxiesQuery } from '../../proxies/proxiesApi';
import { ScrapeMethod, Site } from '../types';

import { AttrSelectors } from './AttrSelectorField';
import { FocusTherapyConfig } from './FocusTherapyConfig';
import { HtmlScrapeConfig } from './HtmlScrapeConfig';
import { SearchableConfig } from './SearchableConfig';

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

export function ScrapeMethodConfiguration({ initialValues }: { initialValues: Partial<Site> }) {
  const currentScrapeMethod: ScrapeMethod = Form.useWatch('scrape_method');
  return (
    <Form.Item name="scrape_method_configuration">
      {currentScrapeMethod === ScrapeMethod.Html && <HtmlScrapeConfig />}
      <DocumentExtensions />
      <UrlKeywords />
      <AttrSelectors
        displayIsResource
        parentName={['scrape_method_configuration', 'attr_selectors']}
        title={<label className="font-semibold">Custom Selectors</label>}
      />
      <SearchableConfig />
      <ProxyExclusions />
      <WaitFor />
      <WaitForTimeout />
      <SearchInFrames />
      <AllowDocDocUpdate />
      <FocusTherapyConfig initialValues={initialValues} />
    </Form.Item>
  );
}

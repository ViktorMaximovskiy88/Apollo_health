import { Input, Form, Select, Tooltip, Switch, Checkbox } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

import { useGetProxiesQuery } from '../../proxies/proxiesApi';
import { ScrapeMethod } from '../types';

export function CmsDocTypes() {
  const scrapeMethod: ScrapeMethod = Form.useWatch(['scrape_method']);
  const docTypes = [
    { value: 1, label: 'NCD' },
    { value: 2, label: 'LCD' },
    { value: 3, label: 'LCA' },
  ];

  return (
    <>
      {scrapeMethod === ScrapeMethod.CMS ? (
        <Form.Item
          name={['scrape_method_configuration', 'cms_doc_types']}
          label="CMS Document Types"
        >
          <Checkbox.Group options={docTypes} className="flex" />
        </Form.Item>
      ) : (
        <></>
      )}
    </>
  );
}

export function DocumentExtensions() {
  const extensions = [
    { value: 'pdf', label: 'PDF (.pdf)' },
    { value: 'xlsx', label: 'Excel (.xlsx)' },
    { value: 'xls', label: 'Excel (.xls)' },
    { value: 'docx', label: 'Word (.docx)' },
    { value: 'doc', label: 'Word (.doc)' },
    { value: 'html', label: 'HTML (.html)' },
    { value: 'csv', label: 'CSV (.csv)' },
    { value: 'txt', label: 'TXT (.txt)' },
  ];

  return (
    <Form.Item
      name={['scrape_method_configuration', 'document_extensions']}
      label="Document Extensions"
    >
      <Checkbox.Group options={extensions} className="flex flex-col space-y-2" />
    </Form.Item>
  );
}

export function UrlKeywords() {
  return (
    <Form.Item name={['scrape_method_configuration', 'url_keywords']} label="URL Keywords">
      <Select mode="tags" />
    </Form.Item>
  );
}

export function ProxyExclusions() {
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

export function WaitForText() {
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

export function WaitForSelector() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'wait_for_selector']}
      label={
        <>
          <span style={{ marginRight: '5px' }}>Wait For Selector</span>
          <Tooltip
            placement="right"
            title="Collection will wait for specific selector to appear before continuing."
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Input />
    </Form.Item>
  );
}

export function WaitForTimeout() {
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
      rules={[{ required: true, message: 'Required' }]}
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

export function SearchInFrames() {
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

export function PromptButtonSelector() {
  return (
    <Form.Item
      name={['scrape_method_configuration', 'prompt_button_selector']}
      label={
        <>
          <span style={{ marginRight: '5px' }}>Prompt Button Selector</span>
          <Tooltip
            placement="right"
            title="The result of this selector is clicked. It is used to continue during after a site prompt."
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      }
    >
      <Input />
    </Form.Item>
  );
}

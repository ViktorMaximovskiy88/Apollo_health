import { Input, Form, Select, Tooltip, Switch, Checkbox } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

import { useGetProxiesQuery } from '../../proxies/proxiesApi';

export function DocumentExtensions() {
  const extensions = [
    { value: 'pdf', label: 'PDF (.pdf)' },
    { value: 'xlsx', label: 'Excel (.xlsx)' },
    { value: 'docx', label: 'Word (.docx)' },
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

export function WaitFor() {
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

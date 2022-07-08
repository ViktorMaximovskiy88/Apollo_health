import { Button, Checkbox, Form, FormInstance, Input, Select, Space, Radio } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Site, CollectionMethod } from './types';
import { useGetProxiesQuery } from '../proxies/proxiesApi';
import { UrlFormFields } from './UrlFormField';

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
    <Form.Item
      name={['scrape_method_configuration', 'url_keywords']}
      label="URL Keywords"
    >
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
    <Form.Item
      name={['scrape_method_configuration', 'proxy_exclusions']}
      label="Proxy Exclusions"
    >
      <Select mode="multiple" options={proxyOptions} />
    </Form.Item>
  );
}

function FollowLinks(props: { followLinks: boolean, form: FormInstance }) {

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
          new Error(
            'You must provide a Link or URL Keyword with Follow Links enabled'
          )
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
            name={[
              'scrape_method_configuration',
              'follow_link_keywords',
            ]}
            label="Follow Link Keywords"
            rules={[
              {
                validator: (field, value) =>
                  validateFollowLinks(field, value),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
          <Form.Item
            className="grow"
            name={[
              'scrape_method_configuration',
              'follow_link_url_keywords',
            ]}
            label="Follow Link URL Keywords"
            rules={[
              {
                validator: (field, value) =>
                  validateFollowLinks(field, value),
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

export function SiteForm(props: {
  onFinish: (user: Partial<Site>) => void;
  initialValues?: Site;
}) {
  const initialFollowLinks =
    props.initialValues?.scrape_method_configuration.follow_links || false;
  const [followLinks, setFollowLinks] = useState<boolean>(initialFollowLinks);
  const [form] = useForm();

  /* eslint-disable no-template-curly-in-string */
  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: '${label} is not a valid url!',
    },
  };
  /* eslint-enable no-template-curly-in-string */

  function setFormState(modified: Partial<Site>) {
    if (modified.scrape_method_configuration?.follow_links !== undefined) {
      setFollowLinks(modified.scrape_method_configuration?.follow_links);
    }
  }

  let initialValues: Partial<Site> | undefined = props.initialValues;
  if (!initialValues) {
    initialValues = {
      scrape_method: 'SimpleDocumentScrape',
      collection_method: CollectionMethod.Automated,
      cron: '0 16 * * *',
      tags: [],
      base_urls: [{ url: '', name: '', status: 'ACTIVE' }],
      scrape_method_configuration: {
        document_extensions: ['pdf'],
        url_keywords: [],
        proxy_exclusions: [],
        follow_links: false,
        follow_link_keywords: [],
        follow_link_url_keywords: [],
      },
    };
  }
  return (
    <Form
      layout="vertical"
      form={form}
      wrapperCol={{
        xs: { span: 24 },
        sm: { span: 24 },
        md: { span: 24 },
        lg: { span: 16 },
        xl: { span: 12 },
      }}
      requiredMark={false}
      onFinish={props.onFinish}
      onValuesChange={setFormState}
      initialValues={initialValues}
      validateMessages={validateMessages}
    >
      <Form.Item name="name" label="Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <UrlFormFields initialValues={props.initialValues} form={form} />
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
              <Form.Item name="scrape_method_configuration">
                <DocumentExtensions />
                <UrlKeywords />
                <ProxyExclusions />
                <FollowLinks followLinks={followLinks} form={form} />
              </Form.Item>
              <Schedule />
            </>
          ) : null
        }
      </Form.Item>
      <Form.Item name="tags" label="Tags">
        <Select mode="tags" />
      </Form.Item>
      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
          <Link to="/sites">
            <Button htmlType="submit">Cancel</Button>
          </Link>
        </Space>
      </Form.Item>
    </Form>
  );
}

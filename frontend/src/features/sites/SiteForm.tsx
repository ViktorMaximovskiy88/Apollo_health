import { Button, Form, Input, Select, Space } from 'antd';
import { LinkOutlined, MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { useForm } from 'antd/lib/form/Form';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ActiveUrlResponse, BaseUrl, Site } from './types';
import { useGetProxiesQuery } from '../proxies/proxiesApi';
import useAccessToken from '../../app/use-access-token';

export function SiteForm(props: {
  onFinish: (user: Partial<Site>) => void;
  initialValues?: Site;
}) {
  const [form] = useForm();
  const [urlValidation, setUrlValidation] = useState<{[id: string]: ActiveUrlResponse}>({});
  const currentSite = props.initialValues ? props.initialValues._id : "";
  const { data: proxies } = useGetProxiesQuery();
  const proxyOptions = proxies?.map((proxy) => ({ label: proxy.name, value: proxy._id }));
  const token = useAccessToken();

  async function validateUrl(key: number, value: string) {
    const checkUrl = encodeURIComponent(value);
    let url = encodeURI(`/api/v1/sites/active-url?url=${checkUrl}`);
    if (currentSite) url += `&currentSite=${currentSite}`;
    const check = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const activeUrlResponse = await check.json();

    setUrlValidation((prevState) => {
      const update = { ...prevState };
      update[key] = activeUrlResponse;
      return update;
    });

    if (activeUrlResponse.in_use) {
      return Promise.reject(new Error('URL is already in use'));
    }

    const baseUrls = form.getFieldsValue().base_urls;
    const duplicateUrls = baseUrls.filter((baseUrl: BaseUrl) => {
      if (baseUrl.url === value) return true;
      return false;
    });

    if (duplicateUrls.length > 1) {
      return Promise.reject(new Error('URL is already in use with this site'));
    }

    return Promise.resolve();
  }

  function createErrorMessage(key: number) {
    const urlCheck = urlValidation[key];
    if (urlCheck?.in_use) {
      return (
        <p>
          URL is in use by <a
            href={`../${urlCheck.site?._id}/scrapes`}
            target='_blank'
            rel='noopener noreferrer'
          >
            {`${urlCheck.site?.name}`}
          </a>
        </p>
      )
    }

    return undefined;
  }

  const hasError = (fieldName: string, fieldIndex: number): boolean => {
    const errors = form.getFieldsError()
    const fieldErrors = errors.filter(({ errors, name }) => {
      const [currentFieldName, currentFieldIndex] = name
      if (!currentFieldName) return false
      if (currentFieldName !== fieldName) return false
      if (currentFieldIndex !== fieldIndex) return false
      return errors.length > 0
    })
    return fieldErrors.length > 0
  };

  const scrapes = [
    { value: 'SimpleDocumentScrape', label: 'Simple Document Scrape' },
    { value: 'BrowserDocumentScrape', label: 'Browser Document Scrape' },
    { value: 'MyPrimeSearchableScrape', label: 'MyPrime Searchable Scrape' },
  ];

  const schedules = [
    { value: '0 16 * * *', label: 'Daily' },
    { value: '0 16 * * 0', label: 'Weekly' },
    { value: '0 16 1 * *', label: 'Monthly' },
  ];

  const extensions = [
    { value: 'pdf', label: 'PDF (.pdf)' },
    { value: 'xlsx', label: 'Excel (.xlsx)' },
    { value: 'docx', label: 'Word (.docx)' },
  ];

  /* eslint-disable no-template-curly-in-string */
  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: '${label} is not a valid url!',
    },
  };
  /* eslint-enable no-template-curly-in-string */

  let initialValues: Partial<Site> | undefined = props.initialValues
  if (!initialValues) {
    initialValues = {
      scrape_method: 'SimpleDocumentScrape',
      cron: '0 16 * * *',
      tags: [],
      base_urls: [{ url: '', name: '', status: 'ACTIVE' }],
      scrape_method_configuration: {
        document_extensions: ['pdf'],
        url_keywords: [],
        proxy_exclusions: [],
      },
    }
  }

  return (
    <Form
      layout="vertical"
      form={form}
      wrapperCol={{ span: 7 }}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={initialValues}
      validateMessages={validateMessages}
    >
      <Form.Item name="name" label="Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.List
        name="base_urls"
      >
        {(fields, { add, remove }, { errors }) => (
          <>
            {fields.map(({ key, name, ...field }, index) => (
              <Form.Item
                key={key}
                className="mb-2"
                {...field}
              >
                <Input.Group className="space-x-2 flex">
                  <Form.Item
                    className="grow mb-0"
                    hasFeedback
                    help={createErrorMessage(key)}
                    {...field}
                    label="URL"
                    name={[name, 'url']}
                    rules={[
                      {
                        required: true,
                        type: 'url',
                      },
                      {
                        validator: ((_, value) => validateUrl(key, value)),
                      }
                    ]}
                    validateTrigger= 'onBlur'
                  >
                    <Input />
                  </Form.Item>

                  <Form.Item
                    {...field}
                    name={[name, 'name']}
                    label="Label"
                    className="mb-0"
                  >
                    <Input />
                  </Form.Item>

                  <Form.Item
                    {...field}
                    name={[name, 'status']}
                    label="Status"
                    className="mb-0"
                  >
                    <Select options={[{ value: 'ACTIVE', label: 'Active' }, { value: 'INACTIVE', label: 'Inactive' }]} />
                  </Form.Item>
                  <Form.Item label=" " shouldUpdate className='mb-0'>
                    {() => (
                      <Button
                        className='p-0 focus:border focus:border-offset-2 focus:border-blue-500'
                        href={form.getFieldValue("base_urls")[index].url}
                        disabled={hasError('base_urls', index)}
                        type="link"
                        target="_blank"
                        rel="noreferrer noopener"
                      >
                        <LinkOutlined
                          className='text-gray-500 hover:text-blue-500 focus:text-blue-500'
                        />
                      </Button>
                    )}
                  </Form.Item>
                  {fields.length > 1 ? (
                    <Form.Item
                      label=" "
                      className="mb-0"
                    >
                      <MinusCircleOutlined
                        className="text-gray-500"
                        onClick={() => remove(name)}
                      />
                    </Form.Item>
                  ) : null}

                </Input.Group>
              </Form.Item>
            ))}
            <Form.Item>
              <Button
                type="dashed"
                onClick={() => add({ url: '', name: '', status: 'ACTIVE' })}
                icon={<PlusOutlined />}
              >
                Add URL
              </Button>
              <Form.ErrorList errors={errors} />
            </Form.Item>
          </>
        )}
      </Form.List>
      <Form.Item name="scrape_method" label="Scrape Method">
        <Select options={scrapes} />
      </Form.Item>
      <Form.Item name="scrape_method_configuration">
        <Form.Item name={["scrape_method_configuration", "document_extensions"]} label="Document Extensions">
          <Select mode="multiple" options={extensions} />
        </Form.Item>
        <Form.Item name={["scrape_method_configuration", "url_keywords"]} label="URL Keywords">
          <Select mode="tags" />
        </Form.Item>
        <Form.Item name={["scrape_method_configuration", "proxy_exclusions"]} label="Proxy Exclusions">
          <Select mode="multiple" options={proxyOptions} />
        </Form.Item>
      </Form.Item>
      <Form.Item name="cron" label="Schedule">
        <Select options={schedules} />
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

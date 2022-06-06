/* eslint-disable no-template-curly-in-string */ // because of antd syntax
import { Button, Form, Input, Select, Space } from 'antd';
import { LinkOutlined, MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { Site } from './types';

export function SiteForm(props: {
  onFinish: (user: Partial<Site>) => void;
  initialValues?: Site;
}) {
  const [form] = useForm();

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

  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: '${label} is not a valid url!',
    },
  };
  const extensions = [
    { value: 'pdf', label: 'PDF (.pdf)' },
    { value: 'xlsx', label: 'Excel (.xlsx)' },
    { value: 'docx', label: 'Word (.docx)' },
  ];

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
              >
                <Input.Group className="space-x-2 flex">
                  <Form.Item
                    {...field}
                    name={[name, 'url']}
                    rules={[{ required: true, type: 'url' }]}
                    label="URL"
                    className="grow mb-0"
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

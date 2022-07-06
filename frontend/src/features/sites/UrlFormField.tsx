import { Button, Form, Input, Select } from 'antd';
import {
  LinkOutlined,
  MinusCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useState } from 'react';
import { ActiveUrlResponse, BaseUrl, Site } from './types';
import { fetchWithAuth } from '../../app/base-api';
import { FormInstance } from 'antd/lib/form/Form';

export function UrlFormFields(props: {
  initialValues?: Site;
  form: FormInstance;
}) {
  const [urlValidation, setUrlValidation] = useState<{
    [id: string]: ActiveUrlResponse;
  }>({});

  const currentSite = props.initialValues ? props.initialValues._id : '';

  async function validateUrl(key: number, value: string) {
    const checkUrl = encodeURIComponent(value);
    let url = encodeURI(`/api/v1/sites/active-url?url=${checkUrl}`);
    if (currentSite) url += `&currentSite=${currentSite}`;
    const check = await fetchWithAuth(url);
    const activeUrlResponse = await check.json();

    setUrlValidation((prevState) => {
      const update = { ...prevState };
      update[key] = activeUrlResponse;
      return update;
    });

    if (activeUrlResponse.in_use) {
      return Promise.reject(new Error('URL is already in use'));
    }

    const baseUrls = props.form.getFieldsValue().base_urls;
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
          URL is in use by{' '}
          <a
            href={`../${urlCheck.site?._id}/scrapes`}
            target="_blank"
            rel="noopener noreferrer"
          >
            {`${urlCheck.site?.name}`}
          </a>
        </p>
      );
    }

    return undefined;
  }

  const hasError = (fieldName: string, fieldIndex: number): boolean => {
    const errors = props.form.getFieldsError();
    const fieldErrors = errors.filter(({ errors, name }) => {
      const [currentFieldName, currentFieldIndex] = name;
      if (!currentFieldName) return false;
      if (currentFieldName !== fieldName) return false;
      if (currentFieldIndex !== fieldIndex) return false;
      return errors.length > 0;
    });
    return fieldErrors.length > 0;
  };
  return (
    <Form.List name="base_urls">
      {(fields, { add, remove }, { errors }) => (
        <>
          {fields.map(({ key, name, ...field }, index) => (
            <Form.Item key={key} className="mb-2" {...field}>
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
                      validator: (_, value) => validateUrl(key, value),
                    },
                  ]}
                  validateTrigger="onBlur"
                >
                  <Input.TextArea autoSize={{ minRows: 1, maxRows: 3 }} />
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
                  <Select
                    options={[
                      { value: 'ACTIVE', label: 'Active' },
                      { value: 'INACTIVE', label: 'Inactive' },
                    ]}
                  />
                </Form.Item>
                <Form.Item label=" " shouldUpdate className="mb-0">
                  {() => (
                    <Button
                      className="p-0 focus:border focus:border-offset-2 focus:border-blue-500"
                      href={props.form.getFieldValue('base_urls')[index].url}
                      disabled={hasError('base_urls', index)}
                      type="link"
                      target="_blank"
                      rel="noreferrer noopener"
                    >
                      <LinkOutlined className="text-gray-500 hover:text-blue-500 focus:text-blue-500" />
                    </Button>
                  )}
                </Form.Item>
                {fields.length > 1 ? (
                  <Form.Item label=" " className="mb-0">
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
  );
}

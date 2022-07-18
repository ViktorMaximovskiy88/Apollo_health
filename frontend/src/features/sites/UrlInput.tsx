import { Form, Input } from 'antd';
import { useState } from 'react';
import { ActiveUrlResponse, BaseUrl, Site } from './types';
import { fetchWithAuth } from '../../app/base-api';
import { FormInstance } from 'antd/lib/form/Form';

function useValidateUrlAndErrorMessage(form: FormInstance, initialValues?: Site) {
  const [urlValidation, setUrlValidation] = useState<{
    [id: string]: ActiveUrlResponse;
  }>({});

  async function validateUrl(fieldKey: number, value: string) {
    const currentSite = initialValues ? initialValues._id : '';
    const checkUrl = encodeURIComponent(value);
    let url = encodeURI(`/api/v1/sites/active-url?url=${checkUrl}`);
    if (currentSite) url += `&currentSite=${currentSite}`;
    const check = await fetchWithAuth(url);
    const activeUrlResponse = await check.json();

    setUrlValidation((prevState) => {
      const update = { ...prevState };
      update[fieldKey] = activeUrlResponse;
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

  function createErrorMessage(fieldKey: number) {
    const urlCheck = urlValidation[fieldKey];
    if (urlCheck?.in_use) {
      return (
        <p>
          URL is in use by{' '}
          <a
            href={`/sites/${urlCheck.site?._id}/scrapes`}
            target="_blank"
            rel="noopener noreferrer"
          >
            {`${urlCheck.site?.name}`}
          </a>
        </p>
      );
    }
    return null;
  }
  return { validateUrl, createErrorMessage };
}

interface UrlInputPropTypes {
  initialValues?: Site;
  fieldKey: number;
  name: number;
  field: { fieldKey?: number };
  form: FormInstance;
}
export function UrlInput({ initialValues, fieldKey, name, field, form }: UrlInputPropTypes) {
  const { validateUrl, createErrorMessage } = useValidateUrlAndErrorMessage(form, initialValues);

  return (
    <Form.Item
      className="grow mb-0"
      hasFeedback
      help={createErrorMessage(fieldKey)}
      {...field}
      label="URL"
      name={[name, 'url']}
      rules={[
        {
          required: true,
          type: 'url',
        },
        {
          validator: (_, value) => validateUrl(fieldKey, value),
        },
      ]}
      validateTrigger="onBlur"
    >
      <Input.TextArea autoSize={{ minRows: 1, maxRows: 3 }} />
    </Form.Item>
  );
}
//

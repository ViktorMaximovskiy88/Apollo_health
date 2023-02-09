import { Form, Select, Switch } from 'antd';
import { useEffect } from 'react';

export function FollowLinks() {
  const form = Form.useFormInstance();
  const followLinks = Form.useWatch(['scrape_method_configuration', 'follow_links']);
  const keywords = Form.useWatch(['scrape_method_configuration', 'follow_link_keywords']);
  const urlKeywords = Form.useWatch(['scrape_method_configuration', 'follow_link_url_keywords']);

  useEffect(() => {
    form.validateFields([['scrape_method_configuration', 'follow_link_keywords']]);
    form.validateFields([['scrape_method_configuration', 'follow_link_url_keywords']]);
  }, [form, keywords, urlKeywords]);

  return (
    <div className="flex space-x-5">
      <Form.Item
        name={['scrape_method_configuration', 'follow_links']}
        label="Follow Links"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      {followLinks && (
        <div className="flex grow space-x-5">
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'follow_link_keywords']}
            label="Follow Link Keywords"
            rules={[
              {
                validator: (_rule, value) => validateFollowLinks(value, urlKeywords),
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
                validator: (_rule, value) => validateFollowLinks(value, keywords),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'scrape_base_page']}
            label="Scrape Base Page"
            tooltip="Scrape base url if enabled. Only scrape pages found by follow links if disabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </div>
      )}
    </div>
  );
}

function validateFollowLinks(value: string[], otherField: string[]) {
  if (value.length || otherField.length) {
    return Promise.resolve();
  }
  return Promise.reject(new Error('Link or URL Keyword required'));
}

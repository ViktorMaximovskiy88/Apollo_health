import { Form, Select, Switch } from 'antd';

export function FollowLinks() {
  const form = Form.useFormInstance();
  const followLinks = Form.useWatch(['scrape_method_configuration', 'follow_links']);
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
      const otherValue = form.getFieldValue(otherNamePath);

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

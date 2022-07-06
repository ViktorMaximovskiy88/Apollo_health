import { Button, Form, Input, Select, Space } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Site, CollectionMethod, SiteStatus } from './types';
import { UrlFormFields } from './UrlFormField';
import { CollectionMethodComponent } from './CollectionMethod';

function SiteStatusSelect() {
  const siteStatuses = [
    { value: SiteStatus.New, label: 'New' },
    { value: SiteStatus.QualityHold, label: 'Quality Hold' },
    { value: SiteStatus.Inactive, label: 'Inactive' },
    { value: SiteStatus.Online, label: 'Online' },
  ];
  return (
    <Form.Item name="site_status" label="Status">
      <Select options={siteStatuses} />
    </Form.Item>
  );
}

export function SiteForm(props: { onFinish: (user: Partial<Site>) => void; initialValues?: Site }) {
  const initialFollowLinks = props.initialValues?.scrape_method_configuration.follow_links || false;
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
      site_status: SiteStatus.New,
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

  const wrapperCol = {
    xs: { span: 24 },
    sm: { span: 24 },
    md: { span: 24 },
    lg: { span: 16 },
    xl: { span: 12 },
  };

  return (
    <Form
      layout="vertical"
      form={form}
      wrapperCol={wrapperCol}
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
      <CollectionMethodComponent followLinks={followLinks} form={form} />
      <Form.Item name="tags" label="Tags">
        <Select mode="tags" />
      </Form.Item>
      <SiteStatusSelect />
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
